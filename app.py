from flask import Flask, render_template, request, send_file
import random
import pandas as pd
from faker import Faker
import names
from bson import ObjectId
import uuid
import ulid
import os
import re
import logging
import string


app = Flask(__name__)

column_suggestions = {
    'Salutation': ['Mr.', 'Mrs.', 'Ms.'],
    'First Name': {
        'india': ['male', 'female'],
        'sweden': ['male', 'female'],
        'united_kingdom': ['male', 'female'],
        'usa':['male','female']
    },
    'Last Name': [],
    'Gender': ['Male', 'Female'],
    'Age': [],
    'Marital Status': ['Single', 'Married', 'Divorced'],
    'Occupation': [],
    'Email': ['outlook.com', 'yahoo.com', 'gmail.com', 'hotmail.com', 'bing.com'],
    'Address': ['ip_address', 'street_address'],
    'City': {
        'india': ['Mumbai', 'Delhi', 'Bangalore','Chennai'],
        'sweden': ['Stockholm', 'Gothenburg', 'Malmo'],
        'united_kingdom': ['London', 'Manchester', 'Birmingham'],
        'usa': ['New York', 'Los Angeles', 'Chicago', 'Houston'] 
        
    },
    'Postal Code': {
        'india': {'format': '######'},
        'sweden': {'format': '#####'},
        'united_kingdom': {'format': 'AA# #AA'},
        'usa': {'format': '#####-####'}
    },
    'Telephone': {
        'india': {'code': '+91', 'digits': 10},
        'sweden': {'code': '+46', 'digits': 9},
        'united_kingdom': {'code': '+44', 'digits': 10},
        'usa': {'code': '+1', 'digits': 10}
    },
    'ID': ['ULID', 'MongoDB ObjectID', 'App Bundle ID', 'GUID']
}

def generate_fake_data(num_datasets, columns, column_types, custom_column_data, country='india'):
    if country not in column_suggestions['First Name']:
        country = 'united_kingdom'  # Default to UK if the selected country is not available for 'First Name'

    if country == 'india':
        fake = Faker('en_IN')  # Use the 'en_IN' locale for India
    elif country == 'sweden':
        fake = Faker('sv_SE')  # Use the 'sv_SE' locale for Sweden
    elif country == 'usa':
        fake = Faker('en_US') 
    else:
        fake = Faker('en_GB')  # Default to 'en_GB' for United Kingdom

    datasets = []

    for _ in range(num_datasets):
        dataset = {}

        for column in columns:
            column_name = re.sub(r'\W+', '_', column)

            if column == 'Salutation':
                value = column_types.get(column)
            elif column == 'First Name':
                gender_type = column_types.get(column)
                if gender_type:
                    if gender_type == 'male':
                        value = fake.first_name_male()
                    else:
                        value = fake.first_name_female()
                    value = value[:5]  # Generate first name with exact 5 characters
                else:
                    value = None
            elif column == 'Last Name':
                last_name = fake.last_name()[:5] # Generate last name with exact 5 characters
                value = last_name
            elif column == 'Gender':
                value = column_types.get(column)
            elif column == 'Age':
                value = random.randint(18, 65)
            elif column == 'Marital Status':
                marital_status = column_types.get(column)
                if marital_status == 'Single':
                    value = 'Single'
                elif marital_status == 'Married':
                    value = 'Married'
                elif marital_status == 'Divorced':
                    value = 'Divorced'
                else:
                    value = random.choice(column_suggestions[column])
            elif column == 'Occupation':
                value = fake.job()
            elif column == 'Email':
                email_domain = column_types.get(column)
                if email_domain:
                    value = f'{fake.user_name()}@{email_domain}'
                else:
                    value = None
            elif column == 'Address':
                address_type = column_types.get(column)
                if address_type == 'ip_address':
                    value = generate_ip_address()
                elif address_type == 'street_address':
                    value = generate_street_address(country=country)[:20]  # Generate street address with exact 20 characters
                else:
                    value = None
            elif column == 'City':
                city_suggestions = column_suggestions[column].get(country)
                if city_suggestions:
                    value = random.choice(city_suggestions)
                else:
                    value = None
            elif column == 'Postal Code':
                postal_code_info = column_suggestions[column].get(country)
                if postal_code_info:
                    postal_code_format = postal_code_info['format']
                    value = generate_postal_code(postal_code_format, country)
                else:
                    value = None
            elif column == 'Telephone':
                telephone_info = column_suggestions[column].get(country)
                if telephone_info:
                    code = telephone_info['code']
                    digits = telephone_info.get('digits', 10)  # Default to 10 digits if 'digits' key is not present
                    value = f"{code}{''.join(random.choices(string.digits, k=digits))}"
                else:
                    value = None
            elif column == 'ID':
                id_type = column_types.get(column)
                if id_type == 'ULID':
                    value = str(ulid.ulid())
                elif id_type == 'MongoDB ObjectID':
                    value = str(ObjectId())
                elif id_type == 'App Bundle ID':
                    value = generate_app_bundle_id()
                elif id_type == 'GUID':
                    value = str(uuid.uuid4())
                else:
                    value = None
            else:
                value = None  # Handle unsupported columns here

            dataset[column_name] = value

        # Add custom column data to the dataset
        for custom_column, suggestions in custom_column_data.items():
            custom_column_name = re.sub(r'\W+', '_', custom_column)  # Replace spaces and special characters
            custom_column_input_name = f'custom_column_{custom_column_name}'
            custom_column_value = request.form.get(custom_column_input_name)
            if custom_column_value:
                dataset[custom_column_name] = custom_column_value
            else:
                dataset[custom_column_name] = random.choice(suggestions)

        datasets.append(dataset)

    return datasets

def generate_ip_address():
    ip_address = ".".join(str(random.randint(0, 255)) for _ in range(4))
    return ip_address

def generate_street_address(country='india'):
    if country == 'india':
        fake = Faker('en_IN')
    elif country == 'sweden':
        fake = Faker('sv_SE')
    elif country == 'usa':
        fake = Faker('en_US') 
    else:
        fake = Faker('en_GB')  

    return fake.street_address()

def generate_postal_code(format, country='india'):
    if country == 'united_kingdom':
        return generate_uk_postal_code(format)
    elif country == 'sweden':
        return generate_sweden_postal_code(format)
    elif country == 'usa':
        return generate_usa_postal_code(format)
    else:
        return generate_india_postal_code(format)

def generate_india_postal_code(format):
    return ''.join(random.choices(string.digits, k=len(format)))

def generate_sweden_postal_code(format):
    return ''.join(random.choices(string.digits, k=len(format)))

def generate_uk_postal_code(format):
        return ''.join(random.choices(string.digits + string.ascii_uppercase, k=len(format))).replace('#', '9')

def generate_usa_postal_code(format):
        return ''.join(random.choices(string.digits, k=len(format)))





def generate_app_bundle_id():
    app_bundle_id = "App Bundle ID"
    return app_bundle_id

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        num_datasets = int(request.form['num_datasets'])
        country = request.form.get('country', 'india')  # Default to India if no country is selected
        columns = []
        column_types = {}
        custom_column_data = {}

        for i in range(1, 100):
            column_name = request.form.get(f'column_{i}')
            if column_name:
                columns.append(column_name)
                column_type = request.form.get(f'column_{i}_suggestion')
                column_types[column_name] = column_type

        # Add custom column and its suggestions
        for i in range(1, 100):
            custom_column_name = request.form.get(f'custom_column_{i}', '').strip()
            custom_suggestions = request.form.get(f'custom_suggestions_{i}', '').strip()

            custom_suggestions = [suggestion.strip() for suggestion in custom_suggestions.split(',')]
            custom_suggestions = list(filter(None, custom_suggestions))

            if custom_column_name and custom_suggestions:
                # Add custom column and its suggestions to column_suggestions and custom_column_data
                column_suggestions[custom_column_name] = custom_suggestions
                custom_column_data[custom_column_name] = custom_suggestions

        # Generate fake data with custom column data included
        random_datasets = generate_fake_data(num_datasets, columns, column_types, custom_column_data, country)

        df = pd.DataFrame(random_datasets)

        download_format = request.form.get('download_format')

        if download_format == 'excel':
            excel_file_path = os.path.join(os.getcwd(), 'data.xlsx')
            df.to_excel(excel_file_path, index=False)
            return send_file(excel_file_path, as_attachment=True)

        elif download_format == 'json':
            json_file_path = os.path.join(os.getcwd(), 'data.json')
            df.to_json(json_file_path, orient='records')
            return send_file(json_file_path, as_attachment=True)

        elif download_format == 'xml':
            xml_file_path = os.path.join(os.getcwd(), 'data.xml')
            df.to_xml(xml_file_path, root_name='Data', row_name='Row')
            return send_file(xml_file_path, as_attachment=True)

        elif download_format == 'notepad':
            notepad_file_path = os.path.join(os.getcwd(), 'data.txt')
            df.to_csv(notepad_file_path, index=False, sep='\t')
            return send_file(notepad_file_path, as_attachment=True)

    return render_template('k.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
