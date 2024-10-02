import pandas as pd

class Solution:
    def __init__(
            self,
            excel_file_path,
            country_hq_sheet_name,
            contacts_sheet_name,
            task1_output_sheet_name,
            task2_output_sheet_name):
        self.excel_file_path = excel_file_path
        self.country_hq_sheet_name = country_hq_sheet_name
        self.contacts_sheet_name = contacts_sheet_name
        self.task1_output_sheet_name = task1_output_sheet_name
        self.task2_output_sheet_name = task2_output_sheet_name
        self.country_hq_df = pd.read_excel(excel_file_path, sheet_name=country_hq_sheet_name)
        self.contacts_df = pd.read_excel(excel_file_path, sheet_name=contacts_sheet_name, header=None)

    # First create a tabular data frame that can be used to solve both task1 and task2
    def process_contacts_individual(self):
        all_contacts_long = pd.DataFrame(columns=['species', 'role', 'superhero', 'HQ', 'Email', 'Invader_Group'])
        
        hq_starts = self.contacts_df[self.contacts_df[0].str.endswith('Headquarter', na=False)].index.tolist()
        hq_starts.append(len(self.contacts_df))
        
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
        
        for i in range(len(hq_starts) - 1):
            hq_name = self.contacts_df.iloc[hq_starts[i], 0]
            hq_data = self.contacts_df.iloc[hq_starts[i] + 1:hq_starts[i + 1]]
            hq_data = hq_data.copy()  # Ensure we are working on a copy
            hq_data.columns = ['species', 'attack_role', 'defense_role', 'healing_role']
            hq_data['HQ'] = hq_name
            

            # Melt the data to long format
            hq_contacts_long = hq_data.melt(id_vars=['species', 'HQ'], var_name='role', value_name='superhero')
            hq_contacts_long = hq_contacts_long.dropna()  # Remove rows with NaN values

            # Generate email addresses
            hq_contacts_long['Email'] = hq_contacts_long['superhero'].apply(
                lambda x: f"{x}@avengers.com" if '@' not in x else x
            )

            # Apply the mapping to get the invader group for each species
            hq_contacts_long['Invader_Group'] = hq_contacts_long['species'].apply(lambda x: invader_groups.get(x, 'unknown/unknown'))
            all_contacts_long = pd.concat([all_contacts_long, hq_contacts_long], ignore_index=True)
            
        
        return all_contacts_long
    
    def task1(self, all_contacts_long_individual):
        country_hq_long = self.country_hq_df.melt(id_vars=['Country Name', 'Country Code'], 
                                            var_name='Species Type', 
                                            value_name='HQ')

        # Merge the reshaped country_HQ data with the contacts data
        merged_data = pd.merge(all_contacts_long_individual, country_hq_long, left_on='HQ', right_on='HQ')

        # Creating the lookup table 
        lookup_df = merged_data.pivot_table(
            index=['Country Code', 'species', 'role'],
            values='Email',
            aggfunc=lambda x: ', '.join(x.unique())
        ).reset_index()
        

        # Separate the emails 
        lookup_df['Email'] = lookup_df['Email'].str.split(', ')
        lookup_df = lookup_df.explode('Email').reset_index(drop=True)
        # Save the result of task1 in the specified file
        with pd.ExcelWriter(self.excel_file_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            lookup_df.to_excel(writer, sheet_name=self.task1_output_sheet_name, index=False)

    def task2(self, all_contacts_long_individual):
        # Initialize the task2 output dataframe
        task2_df_individual = pd.DataFrame(columns=['HQ', 'Species', 'Roles', 'Shorthand', 'Superhero'])

        # Function to map roles to shorthand
        def map_roles_to_shorthand(roles):
            roles_set = set(roles)
            if roles_set == {'attack_role', 'defense_role', 'healing_role'}:
                return 'ADH'
            elif roles_set == {'attack_role', 'defense_role'}:
                return 'AD'
            elif roles_set == {'attack_role', 'healing_role'}:
                return 'AH'
            elif roles_set == {'defense_role', 'healing_role'}:
                return 'DH'
            elif 'attack_role' in roles_set:
                return 'A'
            elif 'defense_role' in roles_set:
                return 'D'
            elif 'healing_role' in roles_set:
                return 'H'
            else:
                return ''

        for hq in all_contacts_long_individual['HQ'].unique():
            hq_data = all_contacts_long_individual[all_contacts_long_individual['HQ'] == hq]
            for species in hq_data['species'].unique():
                species_data = hq_data[hq_data['species'] == species]
                for superhero in species_data['superhero'].dropna().unique():
                    # Correctly assign roles and shorthand only for present roles
                    superhero_roles = species_data[species_data['superhero'] == superhero]['role'].unique()
                    superhero_roles_str = ', '.join(superhero_roles)
                    superhero_shorthand = map_roles_to_shorthand(superhero_roles)
                    task2_df_individual = pd.concat(
                        [task2_df_individual, pd.DataFrame(
                            [{'HQ': hq,
                              'Species': species,
                              'Roles': superhero_roles_str,
                              'Shorthand': superhero_shorthand,
                              'Superhero': superhero}]
                            )], ignore_index=True
                        )
                    
        # Create the final bloated-form DataFrame
        columns = [
            'HQ', 'aliens', 'predators', 'd&d_beholder',
            'd&d_devil', 'd&d_lich', 'd&d_treant', 'd&d_mind_flayer',
            'd&d_red_dragon', 'd&d_vampire', 'd&d_werewolf', 'd&d_yuan-ti',
            'd&d_hill_giant']
        
        rows = ['DE-Headquarter', 'US-Headquarter', 'UK-Headquarter', 'Ocean-Headquarter',
                'BRA-Headquarter', 'CAN-Headquarter', 'COL-Headquarter', 'IND-Headquarter',
                'MEX-Headquarter', 'NLD-Headquarter', 'NOR-Headquarter', 'PAK-Headquarter',
                'TUR-Headquarter', 'UAE-Headquarter', 'ARG-Headquarter', 'Aircraft-Headquarter']

        # Initialize the final bloated-form DataFrame
        final_df = pd.DataFrame(columns=columns)

        # Process each superhero and add them to the final DataFrame
        for superhero in task2_df_individual['Superhero'].unique():
            # Create superhero DataFrame
            superhero_df = task2_df_individual[
                task2_df_individual['Superhero'] == superhero
                ].pivot(index='HQ', columns='Species', values='Shorthand').reindex(rows).reset_index()

            # Add missing columns
            for col in columns:
                if col not in superhero_df.columns:
                    superhero_df[col] = ''

            # Ensure the order of columns
            superhero_df = superhero_df[columns]

            # Add superhero name as a separate header row
            header_row = pd.DataFrame([[superhero] + columns[1:]], columns=columns)
            final_df = pd.concat([final_df, header_row, superhero_df, pd.DataFrame([[''] * len(columns)], columns=columns)], ignore_index=True)

        # Save the result of task2 in the specified file
        with pd.ExcelWriter(self.excel_file_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            final_df.to_excel(writer, sheet_name=self.task2_output_sheet_name, index=False, header=False)


def main():
    solution = Solution(
        excel_file_path='Avengers_vs_Invaders_Challenge.xlsx',
        country_hq_sheet_name='Country_HQ',
        contacts_sheet_name='Contacts',
        task1_output_sheet_name='Task1',
        task2_output_sheet_name='Task2'
    )

    # Process data for both task1 & task2
    all_contacts_long_individual = solution.process_contacts_individual()

    #Task1
    solution.task1(all_contacts_long_individual)

    #Task2
    solution.task2(all_contacts_long_individual)
    
# Run the solution for task1 & task2
if __name__ == "__main__":
    main()