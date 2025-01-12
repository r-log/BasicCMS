from datetime import datetime


class MockMangosDB:
    def __init__(self):
        # Mock realms data
        self.realms = [
            {
                'id': 1,
                'name': 'Onyxia',
                'type': 'wotlk',
                'population': 12000,
                'status': True  # True = online, False = offline
            },
            {
                'id': 2,
                'name': 'Lordaeron',
                'type': 'tbc',
                'population': 0,
                'status': False
            },
            {
                'id': 3,
                'name': 'Icecrown',
                'type': 'wotlk',
                'population': 15000,
                'status': True
            },
            {
                'id': 4,
                'name': 'Blackrock',
                'type': 'tbc',
                'population': 6500,
                'status': True
            },
            {
                'id': 5,
                'name': 'Frostwolf',
                'type': 'tbc',
                'population': 0,
                'status': False
            }
        ]

        # Mock accounts data
        self.accounts = {
            'admin': {
                'id': 1,
                'username': 'admin',
                'email': 'admin@mangos.local',
                'sha_pass_hash': '8301316D0D8448A34FA6D0C6BF1CBFA2B4A1A93A',
                'gmlevel': 3,
                'joindate': datetime(2023, 1, 1)
            }
        }

        # Mock characters data
        self.characters = {
            'admin': [
                {
                    'id': 1,
                    'name': 'Arthas',
                    'class': 2,  # Paladin
                    'race': 1,   # Human
                    'level': 80,
                    'realm': 'Icecrown'
                },
                {
                    'id': 2,
                    'name': 'Thrall',
                    'class': 7,  # Shaman
                    'race': 2,   # Orc
                    'level': 80,
                    'realm': 'Onyxia'
                }
            ]
        }

    def get_realm_status(self):
        """Get status of all realms"""
        return self.realms

    def get_realm_by_id(self, realm_id):
        """Get a specific realm by ID"""
        return next((realm for realm in self.realms if realm['id'] == realm_id), None)

    def get_total_population(self):
        """Get total population across all realms"""
        return sum(realm['population'] for realm in self.realms)

    def get_online_realms(self):
        """Get number of online realms"""
        return len([realm for realm in self.realms if realm['status']])

    def get_account_by_username(self, username):
        """Get account details by username"""
        return self.accounts.get(username.lower())

    def create_account(self, username, email, password_hash, gmlevel=0):
        """Create a new account"""
        if username.lower() in self.accounts:
            return False

        self.accounts[username.lower()] = {
            'id': len(self.accounts) + 1,
            'username': username,
            'email': email,
            'sha_pass_hash': password_hash,
            'gmlevel': gmlevel,
            'joindate': datetime.now()
        }
        return True

    def update_account(self, username, updates):
        """Update account details"""
        if username.lower() not in self.accounts:
            return False

        account = self.accounts[username.lower()]
        for key, value in updates.items():
            if key in account:
                account[key] = value
        return True

    def get_characters_by_username(self, username):
        """Get all characters for a specific account"""
        return self.characters.get(username.lower(), [])

    def print_accounts(self):
        """Debug method to print all accounts"""
        for username, account in self.accounts.items():
            print(f"Username: {username}")
            print(f"Email: {account['email']}")
            print(f"Password Hash: {account['sha_pass_hash']}")
            print(f"GM Level: {account['gmlevel']}")
            print("-" * 50)


# Create a global instance
db = MockMangosDB()
print("\nCurrent accounts in database:")
db.print_accounts()
