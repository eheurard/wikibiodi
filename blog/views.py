from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from blog.models import Company
from .forms import CompanyForm

# Create your views here.
def home (request):
    query = request.GET.get('q')
    if query:
        companies = Company.objects.filter(
            Q(name__icontains=query) |
            Q(ISIN_number__icontains=query) |
            Q(Ticker__icontains=query) |
            Q(sector__icontains=query)
        )
    else:
        companies = Company.objects.all()

       
    return render(request, 'blog/home.html', {'companies': companies, 'query': query})

def add_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CompanyForm()
    return render(request, 'blog/add_company.html', {'form': form})
