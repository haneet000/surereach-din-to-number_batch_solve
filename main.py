import csv
import json
import requests


class SurereachDin:
    def __init__(self):
        self.session = requests.session()

        self.din_surereach = "https://dashboard.surereach.io/din"
        self.din_to_get_url = "https://api.surereach.io/api/v1/surereach/users/mobile-email-from-din"
        self.refresh_token_url = "https://api.surereach.io/api/v1/users/refresh-token"

        self.din_main_header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9'
        }
        self.refresh_token_headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': 'Bearer <your_initial_token>'
        }
        self.input_file = "input_file"
        self.output_file = "output_file"
        self.all_din_data = []

    def read_csv(self):
        with open(self.input_file, 'r', encoding='latin-1') as read_file:
            with open(self.output_file, 'w', encoding='latin-1', newline='') as write_csv:
                self.csv_write = csv.DictWriter(write_csv, fieldnames=['name', 'email_id', 'phone_number'])
                self.csv_write.writeheader()
                file_read = csv.DictReader(read_file)
                for din in file_read:
                    din_ = din.get('DINS')
                    self.all_din_data.append(din_)
                self.process_dins()

    def refresh_token(self):
        main_din_response = self.session.get(self.din_surereach, headers=self.din_main_header)
        if main_din_response.status_code == 200:
            payload = {}
            refresh_token_response = self.session.post(self.refresh_token_url, headers=self.refresh_token_headers,
                                                       data=payload)
            if refresh_token_response.status_code == 200:
                refresh_token_res = refresh_token_response.json()
                access_token = refresh_token_res['data']['access_token']

                din_details_header = {
                    'accept': 'application/json, text/plain, */*',
                    'accept-language': 'en-US,en;q=0.9',
                    'authorization': f'Bearer {access_token}',
                    'referer': 'https://dashboard.surereach.io/',
                    'Cookie': f'refresh_token_cookie={access_token}'
                }
                self.din_details_header = din_details_header
                self.process_dins()
            else:
                print("Failed to refresh token")
        else:
            print("Failed to access DIN main URL")

    def process_dins(self):
        for din in self.all_din_data:
            self.get_all_din_details(din)

    def get_all_din_details(self, din):
        if len(din) == 5:
            full_din = f"000{din}"
        elif len(din) == 6:
            full_din = f"00{din}"
        elif len(din) == 7:
            full_din = f"0{din}"
        else:
            full_din = din

        payload = json.dumps({
            "director_id": full_din
        })

        din_get_details_response = self.session.post(self.din_to_get_url, headers=self.din_details_header,
                                                     data=payload)

        if din_get_details_response.status_code == 401:
            self.refresh_token()
            return

        if din_get_details_response.status_code == 200:
            din_to_get_response_ = din_get_details_response.json()
            name = din_to_get_response_['data']['full_name']
            email_id = din_to_get_response_['data']['email']
            phone_number = din_to_get_response_['data']['phone_no']
        else:
            name = "Not Available"
            email_id = "Not Available"
            phone_number = "Not Available"

        details = {
            'name': name,
            'email_id': email_id,
            'phone_number': phone_number
        }
        self.csv_write.writerow(details)


if __name__ == "__main__":
    obj = SurereachDin()
    obj.read_csv()
