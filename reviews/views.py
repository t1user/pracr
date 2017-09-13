from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse, reverse_lazy
from django.views.generic import (UpdateView, DeleteView, CreateView,
                                  ListView, DetailView)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.conf import settings




from .models import Company, Salary, Review, Interview, Profile, Position
from .forms import (CompanySearchForm, CompanyCreateForm, PositionForm,
                    ReviewForm, SalaryForm, InterviewForm,
                    CreateProfileForm_user, CreateProfileForm_profile)



class HomeView(View):
    form_class = CompanySearchForm
    template_name = 'reviews/home.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name,
                      {'form': form})


class CompanySearchView(View):
    form_class = CompanySearchForm
    initial = {}
    template_name = 'reviews/home.html'
    redirect_template_name = 'reviews/company_search_results.html'
    #redirects back to itself
    redirect_view = 'company_search'

    def get(self, request, *args, **kwargs):
        """Used to display both:  search form or search results."""
        search_results = ''
        searchterm_joined = kwargs.get('searchterm')
        searchterm = searchterm_joined.replace('_', ' ')
        if searchterm:
            search_results = Company.objects.filter(name__icontains=searchterm)
            self.template_name = self.redirect_template_name
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name,
                      {'form': form,
                       'search_results': search_results,
                       'searchterm': searchterm,
                       'searchterm_joined': searchterm_joined})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            searchterm = form.cleaned_data['company_name'].replace(' ', '_')
            return HttpResponseRedirect(reverse(self.redirect_view,
                                                kwargs={'searchterm': searchterm}))
        return render(request, self.template_name, {'form': form})


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'reviews/company_view.html'
    context_object_name = 'company'
    item_data = {'review':
                 {'object': Review,
                  'name': 'recenzje',
                  'file': 'reviews/review_item.html',
                  },
                 'salary':
                 {'object': Salary,
                  'name': 'zarobki',
                  'file':  'reviews/salary_item.html',
                  },
                 'interview':
                 {'object': Interview,
                  'name': 'interview',
                  'file':  'reviews/interview_item.html',
                  },
                 }

    def get_items(self, **kwargs):
        items = {}
        for key, value in self.item_data.items():
            object = self.object.get_objects(value['object'])
            count = object.count()
            last = object.last()
            try:
                scores = last.get_scores()
                stars = self.get_stars(scores)
            except:
                stars = {}
            name = value['name']
            file = value['file']
            items[key] = {'count': count,
                          'last': last,
                          'name': name,
                          'file': file,
                          'stars': stars,
                          }
        return items

    def get_stars(self, scores):
        """Calculate number of full, half and blank rating stars for a given dictionary of scores. The dictionary 'scores' has to be in the format:
        {'overallscore': overallscore,
         'advancement': advancement,
         'worklife': worklife,
         'compensation': compensation,
         'environment': environment,} """
        rating_items = {}
        for key, value in scores.items():
            truncated = int(value)
            half = value - truncated
            if 0.25 <= half < 0.75:
                half = 1
            else:
                half = 0
            if value - truncated >= 0.75:
                truncated += 1
            full = range(truncated)
            blank = range(5 - truncated - half)
            # add field names to context to allow for looping over rating
            # items
            label = self.object._meta.get_field(key).verbose_name
            rating_items[key] = {'rating': value,
                                 'full': full,
                                 'half': half,
                                 'blank': blank,
                                 'label': label}
        return rating_items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scores = self.object.get_scores()
        if scores:
            context['stars'] = self.get_stars(scores=scores)
        context['items'] = self.get_items()
        return context


class CompanyItemsView(CompanyDetailView):
    """Used to display lists of reviews/salaries/interviews."""
    template_name = 'reviews/company_items_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.kwargs['item']
        if item in self.item_data:
            item_data = self.item_data[item]
            context['item'] = item
            context['file'] = item_data['file']
            context['name'] = item_data['name']
            item_list = self.object.get_objects(item_data['object']).order_by('-date')
            try:
                data = {x: self.get_stars(x.get_scores())
                        for x in item_list}
            except:
                data = {x: {} for x in item_list}
            context['data'] = data

            context['buttons'] = {x: self.item_data[x]['name']
                                  for x in self.item_data.keys() if x != item}
            return context
        else:
            raise Http404

class CompanyCreate(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyCreateForm
    initial = {'website': 'http://www.'}

    def get(self, request, **kwargs):
        company_name_joined = self.kwargs.get('company')
        company_name = company_name_joined.replace('_', ' ').title()
        self.initial['name'] = company_name
        return super().get(request, **kwargs)

    def form_valid(self, form):
        form.instance.headquarters_city = form.instance.headquarters_city.title()
        return super().form_valid(form)

    def form_invalid(self, form, **kwargs):
        """In case there's an attempt to create a non-unique Company,
        the method pulls out the instance(s) of the Company(s)
        that already exist(s) and adds it/them to the context."""
        context = self.get_context_data(**kwargs)
        context['form'] = form
        errorlist = form.errors.as_data()
        form_dict = form.instance.__dict__
        companies = []
        for field, errors in errorlist.items():
            for error in errors:
                if error.code == 'unique':
                    company = Company.objects.get(**{field: form_dict[field]})
                    if company not in companies:
                        companies.append(company)
        context['unique_error'] = companies
        return self.render_to_response(context)


class CompanyUpdate(LoginRequiredMixin, UpdateView):
    model = Company
    fields = ['name', 'headquarters_city', 'website']
    #template_name = 'reviews/company_view.html'


class CompanyDelete(LoginRequiredMixin, DeleteView):
    model = Company
    success_url = reverse_lazy('home')


class ContentInput(LoginRequiredMixin, View):
    content_form_class = ReviewForm
    position_form_class  = PositionForm
    model = Review
    template_name = "reviews/review_form.html"

    def get(self, request, *args, **kwargs):
        content_form = self.content_form_class()
        position_form = self.position_form_class()
        return render(request, self.template_name,
                      {'content_form': content_form,
                       'position_form': position_form})

    def post(self, request, *args, **kwargs):
        content_form = self.content_form_class(request.POST)
        position_form = self.position_form_class(request.POST)
        if content_form.is_valid() and position_form.is_valid():
            content_form.save()
            position_form.save()
            return redirect('register_success')
        return render(request, self.template_name,
                          {'content_form': content_form,
                           'position_form': position_form})


class ContentCreateAbstract(LoginRequiredMixin, CreateView):
    """
    Creates custom CreateView class to be inherited by views creating
    Reviews and Salaries. On top of standard CreateView functionality
    allows for rendering and processing of an additional form, 
    which creates or recalls correct Position object.
    """
    position_form_class = PositionForm

    def get_context_data(self, **kwargs):
        """
        Adds to context Company object as well as second
        form called 'position_form'.
        """
        context = super().get_context_data(**kwargs)
        self.company = get_object_or_404(Company, pk=self.kwargs['id'])
        context['company'] = self.company
        context['form'].instance.company = self.company
        if 'position_form' not in kwargs and self.two_forms():
            position_form = self.get_position_form()
            position_form.instance.company = self.company
            context['position_form'] = position_form
        return context

    def get_position_instance(self):
        """
        If user has a position associated with the Company
        they're trying to review, this instance should be 
        associated with the review.
        """
        try:
            position_instance = Position.objects.filter(company=self.company,
                                                        user=self.request.user)
            return position_instance[0]
        except:
            return None

    def two_forms(self):
        if self.get_position_instance():
            return False
        else:
            return True
        
    def get_position_form(self):
        """
        Return an instance of position_form. Method mirrors
        standard get_form().
        """
        return self.position_form_class(**self.get_form_kwargs())
    
    def post(self, request, *args, **kwargs):
        """
        Handles POST request, instantiating two forms with passed POST
        data and  validating it. is_valid and is_invalid methods 
        have been overriden to handle two forms instead 
        of one. two_forms returns True if the second form is required.
        """
        self.company = get_object_or_404(Company, pk=self.kwargs['id'])
        form = self.get_form()
        if self.two_forms():
            position_form = self.get_position_form()
            if form.is_valid() and position_form.is_valid():
                return self.form_valid(form=form,
                                       position_form=position_form)
            else:
                return self.form_invalid(form=form,
                                         position_form=position_form)
        else:
            return self.form_valid(form=form)
            
    def form_valid(self, form, **kwargs):
        """
        Extends the standard method to save position_form. 
        """
 
        form.instance.user = self.request.user
        form.instance.company = self.company
        if self.two_forms():
            position_form = kwargs['position_form']
            position_form.instance.user = self.request.user
            position_form.instance.company = self.company
            position = position_form.save()
            form.instance.position = position
        else:
            form.instance.position = self.get_position_instance()
        #last two items are direct quotes from super(),
        #broght here only for more explicity
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())
            
    def form_invalid(self, form, position_form):
        """
        Override to enable for handling of both forms. If only one form,
        use superclass.
        """
        if self.two_forms():
            return self.render_to_response(self.get_context_data(form=form,
                                            position_form=position_form))
        else:
            return super().form_valid(form)



class ReviewCreate(ContentCreateAbstract):
    form_class = ReviewForm
    template_name = "reviews/review_form.html"
    
class SalaryCreate(ContentCreateAbstract):
    form_class = SalaryForm
    template_name = "reviews/salary_form.html"
    
class ReviewCreateOld(LoginRequiredMixin, CreateView):
    form_class = ReviewForm
    model = Review

    def form_valid(self, form):
        company = get_object_or_404(Company, pk=self.kwargs['id'])
        form.instance.company = company
        company.overallscore += form.instance.overallscore
        company.advancement += form.instance.advancement
        company.worklife += form.instance.worklife
        company.compensation += form.instance.compensation
        company.environment += form.instance.environment
        company.number_of_reviews += 1
        company.save(update_fields=['overallscore',
                                    'advancement',
                                    'worklife',
                                    'compensation',
                                    'environment',
                                    'number_of_reviews',
                                    ])
        #form.instance.position = form.instance.position.title()
        #form.instance.city = form.instance.city.title()
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = get_object_or_404(
            Company, pk=self.kwargs['id'])
        #context['radios'] = ['overallscore', 'advancement',
        #                     'compensation', 'environment', 'worklife']
        return context


class SalaryCreateOld(LoginRequiredMixin, CreateView):
    form_class = SalaryForm
    model = Salary

    def form_valid(self, form):
        form.instance.company = get_object_or_404(
            Company, pk=self.kwargs['id'])
        # stub value to be replaced with request.user.something
        form.instance.years_experience = 5
        form.instance.city = form.instance.city.title()
        form.instance.position = form.instance.position.title()
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = get_object_or_404(
            Company, pk=self.kwargs['id'])
        return context


class InterviewCreate(LoginRequiredMixin, CreateView):
    form_class = InterviewForm
    model = Interview

    def form_valid(self, form):
        form.instance.company = get_object_or_404(
            Company, pk=self.kwargs['id'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = get_object_or_404(
            Company, pk=self.kwargs['id'])
        return context


class CompanyList(LoginRequiredMixin, ListView):
    model = Company
    context_object_name = 'company_list'

    
class CreateProfileView(LoginRequiredMixin, View):
    """
    View with two forms to fill in missing data in User model and Profile.
    Currently not in use because name is not neccessary.
    """
    user_form_class = CreateProfileForm_user
    profile_form_class = CreateProfileForm_profile
    template_name = "reviews/create_profile.html"

    def get(self, request, *args, **kwargs):
        if request.user.last_name == '':
            user_form = self.user_form_class()
        else:
            user_form = {}
        profile_form = self.profile_form_class()
        return render(request, self.template_name,
                      {'user_form': user_form,
                       'profile_form': profile_form})

    def post(self, request, *args, **kwargs):
        user_form = self.user_form_class(request.POST, instance=request.user)
        profile_form = self.profile_form_class(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('register_success')
        return render(request, self.template_name,
                          {'user_form': user_form,
                           'profile_form': profile_form})
        
            
class LinkedinCreateProfile(LoginRequiredMixin, View):
    """
    Presents forms to a user logged in with linkedin so that they can 
    associate their linkedin position with a Company from the database.
    """
    company_form = CompanyCreateForm
    template_name = "reviews/linkedin_associate.html"
    
    def get(self, request, *args, **kwargs):
        companies = request.session.get('companies')
        objects = {}
        for company in companies:
            try:
                company_db = Company.objects.filter(name__icontains=company)
            except:
                pass
            objects[company] = company_db
        return render(request, self.template_name,
                      {'objects': objects})
    
        
