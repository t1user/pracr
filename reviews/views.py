import hashlib
from pprint import pprint

from django.conf import settings
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy, resolve
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView, RedirectView)
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Q

from users.models import Visit

from .forms import (CompanyCreateForm, CompanySearchForm, CompanySelectForm,
                    InterviewForm, PositionForm, ReviewForm, SalaryForm)
from .models import Company, Interview, Position, Review, Salary


def success_message(request):
    """
    Used to display flash message after succesful submission of a form
    """
    messages.add_message(request, messages.SUCCESS, 'Zapisano dane. Dzięki!')

class AccessBlocker(UserPassesTestMixin):
    """
    Works with UserPassesTestMixin to block access to certain views for users
    who haven't contributed to the site yet. Redirection site (login_url) 
    should explain what kind of contribution user has to make to get 
    full access.
    """
    login_url = reverse_lazy('please_contribute')
    
    def test_func(self):
        return self.request.user.profile.contributed

class SuperuserAccessBlocker(UserPassesTestMixin):
    """
    Limits access to the view to superusers only.
    """
    raise_exception = True
    
    def test_func(self):
        return self.request.user.is_superuser

class PleaseContributeView(LoginRequiredMixin, TemplateView):
    """
    User redirected to this view if blocked from viewing a view that
    requires contribution. The template should explain what contribution
    is required to get full access.
    """
    
    template_name = 'reviews/please_contribute.html'


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
    #after search redirects back to itself to present results
    redirect_view = 'company_search'

    def get(self, request, *args, **kwargs):
        """Used to display both:  search form or search results."""
        #this is used by jQuery autocomplete function
        if request.is_ajax():
            search_results = self.get_results(request.GET.get('term',''))
            options = []
            for item in search_results:
                search_item = {'id': item.pk,
                               'label': item.name,
                               'value': item.name}
                options.append(search_item)
            return JsonResponse(options, safe=False)
        #this is used by regular http requests
        search_results = ''
        searchterm_joined = kwargs.get('searchterm')
        searchterm = searchterm_joined.replace('_', ' ')
        if searchterm:
            search_results = self.get_results(searchterm)
            self.template_name = self.redirect_template_name
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name,
                      {'form': form,
                       'search_results': search_results,
                       'searchterm': searchterm,
                       'searchterm_joined': searchterm_joined})

    def get_results(self, searchterm):
        """Fire database query and returns matching Company objects."""
        return Company.objects.filter(Q(name__unaccent__icontains=searchterm) |
                                      Q(website__unaccent__icontains=searchterm))
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            searchterm = form.cleaned_data['company_name'].replace(' ', '_')
            return HttpResponseRedirect(reverse(self.redirect_view,
                                                kwargs={'searchterm': searchterm}))
        return render(request, self.template_name, {'form': form})


class NoSlugRedirectMixin:
    """
    If view called by GET without a slug, redirect to url with slug. Otherwise, ignore.
    Must be inherited by a CBV, which implements get_object() method.
    """
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if kwargs.pop('slug') != self.object.slug:
            args = request.META.get('QUERY_STRING', '')
            if args:
                args = '?{}'.format(args)
            url = reverse(resolve(request.path_info).url_name,
                          kwargs={'slug':self.object.slug, **kwargs}) + args
            return redirect(url)
        else:
            return super().get(request, *args, **kwargs)
    
class CompanyDetailView(LoginRequiredMixin, NoSlugRedirectMixin, DetailView):
    """
    Display Company details with last item of each Review, Salary, Interview. 
    The class ss inherited by CompanyItemsView, which displays lists of all items 
    (Review, Salary, Interview). Company objects are looked up by pk, slug
    is added at the end of url for seo, but is not used for lookup.
    """
    model = Company
    template_name = 'reviews/company_view.html'
    context_object_name = 'company'

    def get_context_data(self, **kwargs):
        """
        Record visit and 
        add items that will  help looping in templates.
        """
        self.record_visit()
        context = super().get_context_data(**kwargs)
        context['items'] = {
            'review': self.object.reviews,
            'salary': self.object.salaries,
            'interview': self.object.interviews,
        }
        return context

    def record_visit(self):
        """
        Record user who visited the Company (date
        of the visit added by model).
        """
        Visit.objects.create(company=self.object,
                      user=self.request.user.profile)


class CompanyItemsRedirectView(RedirectView):
    """A helper function to facilitate accessing xxx_items from templates."""
    pass


class CompanyItemsView(LoginRequiredMixin, AccessBlocker,
                       SingleObjectMixin,  ListView):
    template_name = 'reviews/company_items_view.html'
    paginate_by = 5
    
    def get(self, request, *args, **kwargs):
        """
        Provide Company object for SingleObjectMixin. Redirect if called 
        without slug. Cannot inherit NoSlugRedirectMixin because of MRO clash.
        """
        self.object = self.get_object(queryset=Company.objects.all())
        return self.no_slug(request, *args, **kwargs)
    
    def no_slug(self, request, *args, **kwargs):
        """
        Check if view has been called with proper slug, if not redirect.
        """
        if kwargs.pop('slug') != self.object.slug:
            args = request.META.get('QUERY_STRING', '')
            if args:
                args = '?{}'.format(args)
            url = reverse(resolve(request.path_info).url_name,
                          kwargs={'slug':self.object.slug, **kwargs}) + args
            return redirect(url)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['buttons'] = [x._meta.verbose_name_plural.lower()
                              for x in [Review, Salary, Interview]
                              if x != self.model]
        context['name'] = self.model._meta.verbose_name_plural
        context['model'] = self.model._meta.model_name
        return context
        
    def get_queryset(self):
        return self.object.get_items(self.model).order_by('-date')

    
class ReviewItemsView(CompanyItemsView):
    """Display list of reviews for a given Company."""
    model = Review

    
class SalaryItemsView(CompanyItemsView):
    """Display list of salaries for a given Company."""
    model = Salary


class InterviewItemsView(CompanyItemsView):
    """Display list of interviews for a given Company."""
    model = Interview


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
        # this is typically done in superclass, doing it here gives access to newly created object
        self.object = form.save()
        # this is used if sent here by LinkedInAssociateView
        new_names = self.request.session.get('new_names')
        if new_names:
            current_company = self.kwargs.get('company')
            for name in new_names:
                if current_company == name[1]:
                    position = Position.objects.get(company_name=current_company)
                    position.company = self.object
                    position.save(update_fields=['company'])
                    new_names.remove(name)
                    self.request.session['new_names'] = new_names
            try:
                new_name = new_names.pop()
                self.success_url = new_name[1]
            except:
                pass
        # calling superclass is unnessesary as all it does is self.object=form.save()
        # (done above) plus the redirect below
        return HttpResponseRedirect(self.get_success_url())


    def form_invalid(self, form, **kwargs):
        """
        In case there's an attempt to create a non-unique Company,
        the method pulls out the instance(s) of the Company(s)
        that already exist(s) and adds it/them to the context.
        """
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


class CompanyUpdate(LoginRequiredMixin, SuperuserAccessBlocker, UpdateView):
    model = Company
    fields = ['name', 'headquarters_city', 'website']
    #template_name = 'reviews/company_view.html'


class CompanyDelete(LoginRequiredMixin, SuperuserAccessBlocker, DeleteView):
    model = Company
    success_url = reverse_lazy('home')


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
        If user has a position associated with the Company they're trying to review, 
        this Position instance should be associated with the review.
        TODO:
        PROPERLY HANDLE MORE THAN ONE POSITION INSTANCE.
        """
        position_instance = Position.objects.filter(company=self.company,
                                                    user=self.request.user)
        if position_instance:
            return position_instance[position_instance.count()-1]

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
        Instantiate two forms with passed POST data and validate them. 
        is_valid and is_invalid methods have been overriden to handle two forms.
        """
        self.object = None
        self.company = get_object_or_404(Company, pk=self.kwargs['id'])
        form = self.get_form()
        #returns True if the second form is required.
        if self.two_forms():
            position_form = self.get_position_form()
            if form.is_valid() and position_form.is_valid():
                return self.form_valid(form=form,
                                       position_form=position_form)
            else:
                return self.form_invalid(form=form,
                                         position_form=position_form)
        else:
            if form.is_valid():
                return self.form_valid(form=form)
            else:
                return self.form_invalid(form=form)

            
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
        # give user full access to views that require contribution to the site
        self.request.user.profile.contributed = True
        self.request.user.profile.save(update_fields = ['contributed'])
        success_message(self.request)
        return HttpResponseRedirect(self.get_success_url())
            
    def form_invalid(self, form, **kwargs):
        """
        Handle two forms. If only one form profided, use superclass.
        """
        if self.two_forms():
            position_form = kwargs['position_form']
            return self.render_to_response(self.get_context_data(form=form,
                                            position_form=position_form))
        else:
            return super().form_invalid(form, **kwargs)


class TokenVerifyMixin:
    """
    Prevent resubmission of the same of form. After saving form data, store 
    hashed csrf in session. On form submission check its csrf against the one
    stored in session.
    """
    def post(self, request, *args, **kwargs):
        """
        Check for resubmission of the same form.
        """
        if self.check_token():
            self.company = get_object_or_404(Company, pk=self.kwargs['id'])
            return redirect(self.company)
        return super().post(request, *args, **kwargs)

    def hash_token(self):
        """
        Get csrf token and hash it.
        """
        token = self.request.POST.get('csrfmiddlewaretoken')
        hash = hashlib.sha1(token.encode('utf-8')).hexdigest()
        return hash
    
    def save_token(self):
        """
        Store hashed csrf token in session, so that track can be kept on which
        forms have already been saved to database. Allows for prevention of
        multiple submissions of the same form.
        """
        self.request.session['token'] = self.hash_token()
        
    def check_token(self):
        """
        Compare csrf token with the one stored in session.
        """
        token = self.hash_token()
        stored_token = self.request.session.get('token')
        if token == stored_token:
            return True

    def form_valid(self, *args, **kwargs):
        """
        Store csrf token in session.
        """
        self.save_token()
        return super().form_valid(*args, **kwargs)
    

class ReviewCreate(TokenVerifyMixin, ContentCreateAbstract):
    form_class = ReviewForm
    template_name = "reviews/review_form.html"

    
class SalaryCreate(TokenVerifyMixin, ContentCreateAbstract):
    form_class = SalaryForm
    template_name = "reviews/salary_form.html"
    

class InterviewCreate(LoginRequiredMixin, TokenVerifyMixin, CreateView):
    form_class = InterviewForm
    model = Interview

    def form_valid(self, form):
        form.instance.company = get_object_or_404(
            Company, pk=self.kwargs['id'])
        success_message(self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = get_object_or_404(
            Company, pk=self.kwargs['id'])
        return context


class CompanyList(LoginRequiredMixin, SuperuserAccessBlocker, ListView):
    model = Company
    context_object_name = 'company_list'
    paginate_by = 20

                
class LinkedinCreateProfile(LoginRequiredMixin, View):
    """
    Presents forms to a user logged in with linkedin so that they can 
    associate their linkedin position with a Company from the database.
    """
    form_class = CompanySelectForm
    template_name = "reviews/linkedin_associate.html"
    
    def get(self, request, *args, **kwargs):
        # we are redirected here by social_pipeline_override.py
        # session should have unassociated company names
        # companies is a list of tuples of (position.id, company_name)
        companies = request.session['companies']
        names = [name[1] for name in companies]
        print('from session: ', companies)
        candidates = {}
        new_names = []
        for company in companies:
            print('iteration: ', company)
            company_db = Company.objects.filter(name__icontains=company[1])
            if company_db.count() > 0:
                # candidates are companies that have database entries similar
                # to their names, user is suggested to chose an association
                # candidates[company_name] = (position_id, company_name, company_db)
                candidates[company[1]] = (company[0], company[1], company_db) 
            else:
                # new names are names that haven't been found in the database
                # so potentially they have to be appended, user will be given 
                # an option to get redirected to a form creating new company
                new_names.append(company)
                pass
        request.session['new_names'] = new_names
        forms = {}
        if candidates:
            print(candidates)
            form_choices = {}
            # company_tuple is a tuple of (position_id, company_name, company_db)
            for candidate, company_tuple in candidates.items():
                # will be used as choices parameter on the form
                choices = [(company.pk, company.name) for company in company_tuple[2]]
                print('candidate: ', candidate)
                print('options: ', companies)
                forms[candidate] = self.form_class(companies=choices,
                                                   prefix=candidate,
                                                   initial={'position': company_tuple[0]})
                form_choices[candidate] = choices
            request.session['form_choices'] = form_choices
        #else:
            #request.session['new_names'] = new_names
        print('companies: ', companies, 'candidates: ', candidates, 'new_names: ', new_names, 'forms: ', forms)
        return render(request, self.template_name,
                      {'companies': names,
                       'candidates': candidates,
                       'new_names': new_names,
                       'forms': forms})

    def post(self, request, *args, **kwargs):
        form_choices = request.session['form_choices']
        forms = {}
        valid = True
        for candidate, choices in form_choices.items():
            form = self.form_class(request.POST,
                                   companies=choices,
                                   prefix=candidate)
            if not form.is_valid():
                valid = False
            forms[candidate] = form
        if valid:
            new_names = []
            for name, form in forms.items():
                company_pk = form.cleaned_data.get('company_name')
                if company_pk == 'None':
                    company_pk = None
                position_pk = form.cleaned_data.get('position')
                position = Position.objects.get(pk=position_pk)
                print(company_pk is None)
                if company_pk:
                    print('I am inside')
                    company = Company.objects.get(pk=company_pk)
                    position.company = company
                    position.save(update_fields=['company'])
                else:
                    new_names.append((position.id, name))
 
            
            if request.session.get('new_names') or new_names:
                request.session['new_names'] += new_names

            print('new_names: ', request.session.get('new_names'))                
            if request.session['new_names']:
                index = len(request.session['new_names']) - 1
                return redirect('company_create', company=request.session['new_names'][index][1])
            else:
                return redirect('home')
        else:
            print(forms)
            return render(request, self.template_name,
                          {'forms': forms})

