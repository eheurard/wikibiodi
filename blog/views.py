import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
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
            df = pd.read_excel(file, engine='openpyxl')

            success_count = 0
            company_not_found = 0
            asset_already_exists = 0
            other_errors = 0
            error_messages = []

            for _, row in df.iterrows():
                owner_1 = None
                if pd.notna(row["Owner_1"]):
                    owner_1 = Company.objects.filter(name__iexact=row["Owner_1"].strip()).first()

                if not owner_1:
                    company_not_found += 1
                    error_messages.append(f"Company '{row['Owner_1']}' not found.")
                    continue

                asset_name = row["Name"].strip() if pd.notna(row["Name"]) else None
                existing_asset = Asset.objects.filter(name__iexact=asset_name, owner_1=owner_1).exists()

                if existing_asset:
                    asset_already_exists += 1
                    error_messages.append(f"Asset '{asset_name}' already exists for company '{owner_1.name}'.")
                    continue

                try:
                    Asset.objects.create(
                        name=asset_name,
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
                    success_count += 1
                except Exception as e:
                    other_errors += 1
                    error_messages.append(f"Error creating asset '{asset_name}': {str(e)}")

            # Display success and errors with Django messages
            if success_count > 0:
                messages.success(request, f"Successfully uploaded {success_count} assets.")

            if company_not_found > 0:
                messages.warning(request, f"{company_not_found} assets couldn't be added because the company does not exist.")

            if asset_already_exists > 0:
                messages.warning(request, f"{asset_already_exists} assets already exist and were skipped.")

            if other_errors > 0:
                messages.error(request, f"{other_errors} assets encountered errors. See details below.")

            for error in error_messages[:5]:  # Show up to 5 errors in messages
                messages.error(request, error)

            return redirect("upload_assets")

    else:
        form = AssetUploadForm()

    return render(request, "blog/upload_assets.html", {"form": form})

def delete_company(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    
    if request.method == "POST":
        company.delete()
        return redirect("home")  # Redirect to home after deletion
    
    return redirect("company_general", company_id=company_id)