import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from blog.models import Company, Asset
from .forms import CompanyForm, AssetUploadForm, CompanyUploadForm

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


def upload_data(request):
    if request.method == "POST":
        asset_form = AssetUploadForm(request.POST, request.FILES)
        company_form = CompanyUploadForm(request.POST, request.FILES)

        # Track success & error counts
        success_assets = 0
        success_companies = 0
        company_already_exists = 0
        asset_already_exists = 0
        other_errors = 0
        error_messages = []

        # Handle Asset Upload
        if 'asset_upload' in request.POST:  # Check for the button name instead of file
            if 'asset_file' in request.FILES:
                file = request.FILES['asset_file']
                try:
                    df = pd.read_excel(file, engine='openpyxl')

                    for _, row in df.iterrows():
                        owner_1 = None
                        if pd.notna(row.get("Owner_1")):  # Use .get() to safely access dictionary
                            owner_1 = Company.objects.filter(name__iexact=row["Owner_1"].strip()).first()

                        if not owner_1:
                            error_messages.append(f"Company '{row.get('Owner_1')}' not found.")
                            other_errors += 1
                            continue

                        asset_name = row.get("Name", "").strip() if pd.notna(row.get("Name")) else None
                        if not asset_name:
                            error_messages.append("Asset name is required.")
                            other_errors += 1
                            continue

                        existing_asset = Asset.objects.filter(name__iexact=asset_name, owner_1=owner_1).exists()
                        
                        if existing_asset:
                            asset_already_exists += 1
                            error_messages.append(f"Asset '{asset_name}' already exists for company '{owner_1.name}'.")
                            continue

                        try:
                            Asset.objects.create(
                                name=asset_name,
                                latitude=row.get("latitude") if pd.notna(row.get("latitude")) else None,
                                longitude=row.get("longitude") if pd.notna(row.get("longitude")) else None,
                                asset_type=row.get("Asset type") if pd.notna(row.get("Asset type")) else None,
                                owner_1=owner_1,
                                ownership_1=row.get("Ownership") if pd.notna(row.get("Ownership")) else None,
                                description=row.get("description") if pd.notna(row.get("description")) else None,
                                water_score=row.get("Water_score") if pd.notna(row.get("Water_score")) else 0,
                                biodiv_score=row.get("biodiv_score") if pd.notna(row.get("biodiv_score")) else 0,
                                social_score=row.get("social_score") if pd.notna(row.get("social_score")) else 0,
                            )
                            success_assets += 1
                        except Exception as e:
                            other_errors += 1
                            error_messages.append(f"Error creating asset '{asset_name}': {str(e)}")
                except Exception as e:
                    messages.error(request, f"Error processing file: {str(e)}")
            else:
                messages.error(request, "Please select a file to upload.")

        # Handle Company Upload
        elif 'company_upload' in request.POST:
            file = request.FILES['company_file']
            df = pd.read_excel(file, engine='openpyxl')

            for _, row in df.iterrows():
                name = row["Nom de l'entreprise"].strip() if pd.notna(row["Nom de l'entreprise"]) else None
                isin = row["Numéro ISIN"].strip() if pd.notna(row["Numéro ISIN"]) else None
                ticker = row["Ticker"].strip() if pd.notna(row["Ticker"]) else None
                sector = row["Secteur"].strip() if pd.notna(row["Secteur"]) else None

                # Check if company already exists (either by name or ISIN)
                if Company.objects.filter(name__iexact=name).exists() or Company.objects.filter(ISIN_number__iexact=isin).exists():
                    company_already_exists += 1
                    error_messages.append(f"Company '{name}' or ISIN '{isin}' already exists.")
                    continue

                try:
                    Company.objects.create(
                        name=name,
                        ISIN_number=isin,
                        Ticker=ticker,
                        sector=sector
                    )
                    success_companies += 1
                except Exception as e:
                    other_errors += 1
                    error_messages.append(f"Error creating company '{name}': {str(e)}")

        # Add messages to Django messages framework
        if success_assets > 0:
            messages.success(request, f"Successfully uploaded {success_assets} assets.")
        if success_companies > 0:
            messages.success(request, f"Successfully uploaded {success_companies} companies.")
        if company_already_exists > 0:
            messages.warning(request, f"{company_already_exists} companies were skipped because they already exist.")
        if asset_already_exists > 0:
            messages.warning(request, f"{asset_already_exists} assets already exist and were skipped.")
        if other_errors > 0:
            messages.error(request, f"{other_errors} errors encountered.")
            for msg in error_messages:
                messages.error(request, msg)

        return redirect("upload_data")

    else:
        asset_form = AssetUploadForm()
        company_form = CompanyUploadForm()

    return render(request, "blog/upload_data.html", {
        "asset_form": asset_form, 
        "company_form": company_form
    })

def delete_company(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    
    if request.method == "POST":
        company.delete()
        return redirect("home")  # Redirect to home after deletion
    
    return redirect("company_general", company_id=company_id)