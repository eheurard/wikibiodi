import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from blog.models import Company, Asset
from .forms import CompanyForm, AssetUploadForm

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

def company_general(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    # get assets where company is mentionned as owner
    assets = Asset.objects.filter(
        owner_1=company
    ) | Asset.objects.filter(
        owner_2=company
    ) | Asset.objects.filter(
        owner_3=company
    )
    return render(request, 'blog/company_general.html', {'company': company, 'assets': assets})


def upload_assets(request):
    if request.method == "POST":
        form = AssetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            
            # Lire le fichier avec Pandas
            df = pd.read_excel(file, engine='openpyxl')

            for _, row in df.iterrows():
                # Récupérer ou créer l'entreprise propriétaire
                owner_1 = None
                if pd.notna(row["Owner_1"]) and pd.notna(row["ISIN"]):
                    owner_1, _ = Company.objects.get_or_create(name=row["Owner_1"], ISIN_number=row["ISIN"])

                # Créer l'asset
                Asset.objects.create(
                    name=row["Name"],
                    latitude=row["latitude"] if pd.notna(row["latitude"]) else None,
                    longitude=row["longitude"] if pd.notna(row["longitude"]) else None,
                    asset_type=row["Asset type"] if pd.notna(row["Asset type"]) else None,
                    owner_1=owner_1,
                    ownership_1=row["Ownership"] if pd.notna(row["Ownership"]) else None,
                    description=row["description"] if pd.notna(row["description"]) else None,
                    water_score=row["Water_score"] if pd.notna(row["Water_score"]) else 0,
                    biodiv_score=row["biodiv_score"] if pd.notna(row["biodiv_score"]) else 0,
                    social_score=row["social_score"] if pd.notna(row["social_score"]) else 0,
                )

            return render(request, "blog/upload_assets.html", {"form": form})

    else:
        form = AssetUploadForm()

    return render(request, "blog/upload_assets.html", {"form": form})

def delete_company(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    
    if request.method == "POST":
        company.delete()
        return redirect("home")  # Redirect to home after deletion
    
    return redirect("company_general", company_id=company_id)