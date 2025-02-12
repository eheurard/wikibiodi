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
            
            # Read the file with Pandas
            df = pd.read_excel(file, engine='openpyxl')
            
            # Keep track of success and error messages
            success_count = 0
            error_messages = []
            
            for _, row in df.iterrows():
                # Check if the company exists
                owner_1 = None
                if pd.notna(row["Owner_1"]):
                    owner_1 = Company.objects.filter(name__iexact=row["Owner_1"].strip()).first()
                
                # Only create the asset if the company exists
                if owner_1:
                    # Check if an asset with the same name already exists for this company
                    asset_name = row["Name"].strip() if pd.notna(row["Name"]) else None
                    existing_asset = Asset.objects.filter(
                        name__iexact=asset_name,
                        owner_1=owner_1
                    ).exists()
                    
                    if existing_asset:
                        error_messages.append(
                            f"Asset '{asset_name}' already exists for company '{owner_1.name}'"
                        )
                        continue
                    
                    # Create the asset if it doesn't exist
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
                        error_messages.append(
                            f"Error creating asset '{asset_name}': {str(e)}"
                        )
            
            # Prepare the response message
            message = f"Successfully uploaded {success_count} assets. "
            if error_messages:
                message += f"\nErrors encountered: \n" + "\n".join(error_messages)
            
            return render(request, "blog/upload_assets.html", {
                "form": form,
                "message": message
            })
    
    else:
        form = AssetUploadForm()
    
    return render(request, "blog/upload_assets.html", {"form": form})

def delete_company(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    
    if request.method == "POST":
        company.delete()
        return redirect("home")  # Redirect to home after deletion
    
    return redirect("company_general", company_id=company_id)