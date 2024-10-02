from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load the data
excel_file_path = 'Avengers_vs_Invaders_Challenge.xlsx'
country_hq_sheet_name = 'Country_HQ'
contacts_sheet_name = 'Contacts'

# Read the Excel sheets i
country_hq_df = pd.read_excel(excel_file_path, sheet_name=country_hq_sheet_name)
contacts_df = pd.read_excel(excel_file_path, sheet_name=contacts_sheet_name, header=None)

# Process contacts to create dataframes
def process_contacts():
    all_contacts_long = pd.DataFrame(columns=['species', 'role', 'superhero', 'HQ', 'Email', 'Invader_Group'])
    task2_df_individual = pd.DataFrame(columns=['HQ', 'Species', 'Roles', 'Shorthand', 'Superhero'])

    # Identify the start of each headquarters section in the contacts DataFrame
    hq_starts = contacts_df[contacts_df[0].str.endswith('Headquarter', na=False)].index.tolist()
    hq_starts.append(len(contacts_df))

    invader_groups = {
        'aliens': 'aliens',
        'predators': 'predators',
        'd&d_beholder': 'beholder/d&d monsters',
        'd&d_devil': 'devil/d&d monsters',
        'd&d_lich': 'lich/d&d monsters',
        'd&d_mind_flayer': 'mind_flayer/d&d monsters',
        'd&d_vampire': 'vampire/d&d monsters',
        'd&d_red_dragon': 'red_dragon/d&d monsters',
        'd&d_hill_giant': 'hill_giant/d&d monsters',
        'd&d_treant': 'treant/d&d monsters',
        'd&d_werewolf': 'werewolf/d&d monsters',
        'd&d_yuan-ti': 'yuan-ti/d&d monsters'
    }

    # Process each headquarters section
    for i in range(len(hq_starts) - 1):
        hq_name = contacts_df.iloc[hq_starts[i], 0]
        hq_data = contacts_df.iloc[hq_starts[i] + 1:hq_starts[i + 1]]
        hq_data = hq_data.copy()
        hq_data.columns = ['species', 'attack_role', 'defense_role', 'healing_role']
        hq_data['HQ'] = hq_name

        # Transform the data to long format
        hq_contacts_long = hq_data.melt(id_vars=['species', 'HQ'], var_name='role', value_name='superhero')
        hq_contacts_long = hq_contacts_long.dropna()

        # Generate email addresses
        hq_contacts_long['Email'] = hq_contacts_long['superhero'].apply(
            lambda x: f"{x}@avengers.com" if '@' not in x else x
        )

        # Map species to invader groups
        hq_contacts_long['Invader_Group'] = hq_contacts_long['species'].apply(lambda x: invader_groups.get(x, 'unknown/unknown'))

        # Merge headquarters data 
        hq_to_country = country_hq_df.set_index('Country Name').stack().reset_index()
        hq_to_country.columns = ['Country', 'Invader', 'HQ']
        hq_to_country = hq_to_country[['HQ', 'Country']]
        
        hq_contacts_long = hq_contacts_long.merge(hq_to_country, on='HQ', how='left')
        
        all_contacts_long = pd.concat([all_contacts_long, hq_contacts_long], ignore_index=True)
        
        # Process roles for each superhero
        for species in hq_data['species'].unique():
            species_data = hq_contacts_long[hq_contacts_long['species'] == species] 
            for superhero in species_data['superhero'].dropna().unique():
                superhero_roles = species_data[species_data['superhero'] == superhero]['role'].unique()
                superhero_roles_str = ', '.join(superhero_roles)
                superhero_roles_set = set(superhero_roles)
                if superhero_roles_set == {'attack_role', 'defense_role', 'healing_role'}:
                    superhero_shorthand = 'ADH'
                elif superhero_roles_set == {'attack_role', 'defense_role'}:
                    superhero_shorthand = 'AD'
                elif superhero_roles_set == {'attack_role', 'healing_role'}:
                    superhero_shorthand = 'AH'
                elif superhero_roles_set == {'defense_role', 'healing_role'}:
                    superhero_shorthand = 'DH'
                elif 'attack_role' in superhero_roles_set:
                    superhero_shorthand = 'A'
                elif 'defense_role' in superhero_roles_set:
                    superhero_shorthand = 'D'
                elif 'healing_role' in superhero_roles_set:
                    superhero_shorthand = 'H'
                else:
                    superhero_shorthand = ''
                task2_df_individual = pd.concat([task2_df_individual, pd.DataFrame([{'HQ': hq_name, 'Species': species, 'Roles': superhero_roles_str, 'Shorthand': superhero_shorthand, 'Superhero': superhero}])], ignore_index=True)
    
    return all_contacts_long, task2_df_individual

# Initialize like counts 
def initialize_like_counts(task2_df_individual):
    return {superhero: 0 for superhero in task2_df_individual['Superhero'].unique()}

all_contacts_long, task2_df_individual = process_contacts()
like_counts = initialize_like_counts(task2_df_individual)

# Generate random trending data
def generate_random_trending_data():
    return list(map(int, np.random.randint(0, 50, size=10)))

@app.route('/')
def index():
    # Render the main index page
    countries = all_contacts_long['Country'].unique()
    invader_species = all_contacts_long['species'].unique()
    roles = all_contacts_long['role'].unique()
    superheroes = task2_df_individual['Superhero'].unique()
    return render_template('index.html', countries=countries, invader_species=invader_species, roles=roles, superheroes=superheroes, show_search=False)

@app.route('/query', methods=['POST'])
def query():
    # Handle query for invader species and roles 
    country = request.form.get('country') or request.form.get('country_text')
    invader_species = request.form.get('invader_species') or request.form.get('invader_species_text')
    role = request.form.get('role') or request.form.get('role_text')

    # Filter data
    filtered_df = all_contacts_long[
        (all_contacts_long['Country'] == country) & 
        (all_contacts_long['species'] == invader_species) & 
        (all_contacts_long['role'] == role)
    ]
    
    emails = filtered_df['Email'].unique().tolist()
    
    # Render the index page 
    countries = all_contacts_long['Country'].unique()
    invader_species_list = all_contacts_long['species'].unique()
    roles = all_contacts_long['role'].unique()
    superheroes = task2_df_individual['Superhero'].unique()
    
    return render_template('index.html', countries=countries, invader_species=invader_species_list, roles=roles, emails=emails, superheroes=superheroes, show_search=False)

@app.route('/dashboard/<superhero>')
def dashboard(superhero):
    # Render the dashboard 
    superhero_data = task2_df_individual[task2_df_individual['Superhero'] == superhero]
    superheroes = task2_df_individual['Superhero'].unique()
    return render_template('dashboard.html', superhero=superhero, data=superhero_data.to_dict(orient='records'), like_counts=like_counts, superheroes=superheroes, show_search=True)

@app.route('/get_trending_data/<superhero>/<role>')
def get_trending_data(superhero, role):
    # Provide random trending data for a specific superhero and role
    trending_data = generate_random_trending_data()
    return jsonify(trending_data)

@app.route('/like/<superhero>', methods=['POST'])
def like(superhero):
    # Increment the like count 
    like_counts[superhero] += 1
    return jsonify(like_counts[superhero])

@app.route('/search_superhero', methods=['POST'])
def search_superhero():
    superhero_name = request.form.get('superhero_text', '').strip().lower()
    if superhero_name:
        matching_superhero = next((hero for hero in task2_df_individual['Superhero'].unique() if hero.lower() == superhero_name), None)
        if matching_superhero:
            return redirect(url_for('dashboard', superhero=matching_superhero))
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
