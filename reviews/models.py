from django.db import models
from django.urls import reverse
from django.conf import settings
import datetime


class ApprovableModel(models.Model):
    """
    Abstract model providing features for entry approval in the admin module.
    """
    approved = models.NullBooleanField('Zatwierdzone', default=None, null=True, blank=True)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Zatwierdzający',
                                 on_delete=models.SET_NULL,
                                 null=True, blank=True, editable=False)
    reviewed_date = models.DateField('Data przeglądu', null=True, blank=True)
    
    
    class Meta:
        abstract = True

class Company(ApprovableModel):
    class Meta:
        verbose_name = "Firma"
        verbose_name_plural = "Firmy"
        ordering = ['name']
        
    EMPLOYMENT = [('A', '<100'), ('B', '101-500'), ('C', '501-1000'),
                  ('D', '1001-5000'), ('E', '5001-10000'), ('F', '>10000')]

    #only three values are required - to make company creation easy for users
    name = models.CharField('nazwa', max_length=100, unique=True)
    headquarters_city = models.CharField('siedziba centrali', max_length=60)
    website = models.URLField('strona www', unique=True)

    #other fields are optional, to be filled-in by admins
    date = models.DateField('Data dodania do bazy', auto_now_add=True, editable=False)
    region = models.CharField('województwo', max_length=40, blank=True, null=True)
    country = models.CharField('kraj', max_length=40, default='Polska')
    employment = models.CharField('zatrudnienie', max_length=1,
                                  choices=EMPLOYMENT, blank=True, null=True)
    public = models.NullBooleanField('notowane', blank=True, null=True)
    ownership = models.CharField('właściciele', max_length=200, blank=True, null=True)

    #rating inputs - not to be edited directly, numbers have to be divided by
    #number of reviews to get to the rating number
    overallscore = models.PositiveIntegerField('Ocena ogólna', editable=False,
                                               default=0)
    advancement = models.PositiveIntegerField('Możliwości rozwoju', editable=False,
                                              default=0)
    worklife = models.PositiveIntegerField('Równowaga praca/życie', editable=False,
                                           default=0)
    compensation = models.PositiveIntegerField('Zarobki', editable=False,
                                               default=0)
    environment = models.PositiveIntegerField('Atmosfera w pracy', editable=False,
                                              default=0)
    number_of_reviews = models.PositiveIntegerField('Liczba ocen', editable=False,
                                                    default=0)

    def get_reviews(self):
        return Review.objects.filter(company=self.pk)

    def get_salaries(self):
        return Salary.objects.filter(company=self.pk)

    def get_interviews(self):
        return Interview.objects.filter(company=self.pk)

    def get_objects(self, object):
        self.object = object
        return object.objects.filter(company=self.pk)

    def get_scores(self):
        """Calculates actual ratings from database fields"""
        self.update_scores()
        if self.number_of_reviews != 0:
            overallscore = round(self.overallscore / self.number_of_reviews, 1)
            advancement = round(self.advancement / self.number_of_reviews, 1)
            worklife = round(self.worklife / self.number_of_reviews, 1)
            compensation = round(self.compensation / self.number_of_reviews, 1)
            environment = round(self.environment / self.number_of_reviews, 1)
            return {'overallscore': overallscore,
                    'advancement': advancement,
                    'worklife': worklife,
                    'compensation': compensation,
                    'environment': environment,
                    }

    def update_scores(self):
        """Recalculates all scores to make them compliant with existing reviews."""
        reviews = self.get_reviews()
        self.overallscore = 0
        self.advancement = 0
        self.worklife = 0
        self.compensation = 0
        self.environment = 0
        self.number_of_reviews = reviews.count()
        for review in reviews:
            self.overallscore += review.overallscore
            self.advancement += review.advancement
            self.worklife += review.worklife
            self.compensation += review.compensation
            self.environment += review.environment
        self.save()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('company_page',
                       kwargs={'pk': self.pk})


class Position(models.Model):
    class Meta:
        verbose_name = "Stanowisko"
        verbose_name_plural = "Stanowiska"
        
    STATUS_ZATRUDNIENIA = [
        ('A', 'Pełen etat'),
        ('B', 'Część etatu'),
        ('C', 'Zlecenie'),
        ('D', 'Samozazatrudnienie'),
        ('E', 'Inne'),
    ]

    years = range(datetime.datetime.now().year, 1970, -1)
    YEARS = [(i, i) for i in years]
    months = range(1, 13)
    MONTHS = [(i, '{:02}'.format(i)) for i in months]
 
    date = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                             on_delete=models.SET_NULL)
    #company_name used to store name before entry is associated with a Company database record
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_linkedin_id=models.CharField(max_length=25, null=True)
    #company used to associate position with Company database record, blank before the association
    company = models.ForeignKey(Company, on_delete=models.SET_NULL,
                                blank=True, null=True)
    linkedin_id = models.PositiveIntegerField(blank=True, null=True)
    location = models.CharField(max_length=50, null=True)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)
    start_date_month = models.PositiveIntegerField(null=True,
                                                   choices=MONTHS, default=None)
    start_date_year = models.PositiveIntegerField(null=True,
                                                  choices=YEARS, default=None)
    employment_status = models.CharField(max_length=1,
                                         choices=STATUS_ZATRUDNIENIA,
                                         default='A')

    def __str__(self):
        if self.company:
            company = str(self.company)
        elif self.company_name:
            company = self.company_name
        else:
            company = ' '
        return self.position + ' - ' + company + ' - ' + self.user.email

class Review(ApprovableModel):
    class Meta:
        verbose_name = "Recenzja"
        verbose_name_plural = "Recenzje"
        
    date = models.DateTimeField('data', auto_now_add=True, editable=False)
    company = models.ForeignKey(Company, verbose_name='firma',
                                on_delete=models.CASCADE, editable=False)
    position = models.ForeignKey(Position, verbose_name='stanowisko',
                                 on_delete=models.SET_NULL,
                                 null=True, blank=True, editable=False)
    title = models.CharField('tytuł', max_length=100)
    pros = models.TextField('zalety', max_length=500)
    cons = models.TextField('wady', max_length=500)
    comment = models.TextField('co należy zmienić', max_length=500, blank=True)

    RATINGS = [(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]
    overallscore = models.PositiveIntegerField('ocena ogólna',
                                               choices=RATINGS, default=None)
    advancement = models.PositiveIntegerField('możliwości rozwoju',
                                              choices=RATINGS, default=None)
    worklife = models.PositiveIntegerField('równowaga praca/życie',
                                           choices=RATINGS, default=None)
    compensation = models.PositiveIntegerField('zarobki',
                                               choices=RATINGS, default=None)
    environment = models.PositiveIntegerField('atmosfera w pracy',
                                              choices=RATINGS, default=None)
    


    def get_scores(self):
        return {'overallscore': self.overallscore,
                'advancement': self.advancement,
                'worklife': self.worklife,
                'compensation': self.compensation,
                'environment': self.environment,
                }

    def get_absolute_url(self):
        return reverse('company_page',
                       kwargs={'pk': self.company.id})

    def __str__(self):
        return 'id_' + str(self.id) + ' - ' + self.company.name + ' - ' + self.title



class Salary(ApprovableModel):
    class Meta:
        verbose_name = "Zarobki"
        verbose_name_plural = "Zarobki"

    PERIOD = [
        ('M', 'miesięcznie'),
        ('K', 'kwartalnie'),
        ('R', 'rocznie'),
        ('G', 'na godzinę'),
    ]
    GROSS_NET = [
        ('G', 'brutto'),
        ('N', 'netto'),
    ]

    date = models.DateTimeField('data', auto_now_add=True, editable=False)
    company = models.ForeignKey(Company, verbose_name= 'firma',
                                on_delete=models.CASCADE, editable=False)
    position = models.ForeignKey(Position, verbose_name="stanowisko",
                                 on_delete=models.SET_NULL,
                                 null=True, blank=True, editable=False)

    currency = models.CharField('waluta',
                                max_length=3, default='PLN')
    salary_input = models.PositiveIntegerField('pensja')
    period = models.CharField('',
                              max_length=1, default='M', choices=PERIOD,
                              blank=True)
    gross_net = models.CharField(
        '', max_length=1, default='G', choices=GROSS_NET, blank=True)

    bonus_input = models.PositiveIntegerField('premia', default=0)
    bonus_period = models.CharField('',
                                    max_length=1, default='R', choices=PERIOD,
                                    blank=True)
    bonus_gross_net = models.CharField('',
                                       max_length=1, default='G', choices=GROSS_NET,
                                       blank=True)

    base_monthly = models.PositiveIntegerField('Pensja zasadnicza miesięcznie',
                                               blank=True,
                                               default=0, editable=False)
    base_annual = models.PositiveIntegerField('Pensja zasadnicza rocznie',
                                              blank=True,
                                              default=0, editable=False)

    total_monthly = models.PositiveIntegerField('Pensja całkowita miesięcznie',
                                                blank=True,
                                                default=0, editable=False)
    total_annual = models.PositiveIntegerField('Pensja całkowita rocznie',
                                               blank=True,
                                               default=0, editable=False)

    def get_absolute_url(self):
        return reverse('company_page',
                       kwargs={'pk': self.company.id})

    def __str__(self):
        return 'id_{}_{}'.format(self.id, self.company)


class Interview(ApprovableModel):
    HOW_GOT = [
        ('A', 'Ogłoszenie'),
        ('B', 'Kontakty profesjonalne'),
        ('C', 'Head-hunter'),
        ('D', 'Znajomi-rodzina'),
        ('E', 'Seks z decydentem'),
        ('F', 'Inne'),
    ]
    DIFFICULTY = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    GOT_OFFER = [
        (True, 'Tak'),
        (False, 'Nie'),
        ]
    
    company = models.ForeignKey(Company,
                                on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, editable=False)
    position = models.CharField('stanowisko',
                                max_length=100, blank=True)
    department = models.CharField('departament',
                                  max_length=100, blank=True)
    how_got = models.CharField('droga do interview',
                               max_length=1, choices=HOW_GOT, default=None)
    difficulty = models.PositiveIntegerField('trudność',
                                             choices=DIFFICULTY, default=None)
    got_offer = models.NullBooleanField('czy dostał ofertę', choices=GOT_OFFER,
                                        blank=True, null=True, default=None)
    questions = models.TextField('pytania')
    impressions = models.CharField('wrażenia',
                                   max_length=100, blank=True)

    def get_absolute_url(self):
        return reverse('company_page',
                       kwargs={'pk': self.company.id})

    def __str__(self):
        return 'id_' + str(self.id)

