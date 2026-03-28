# SI 201 HW4 (Library Checkout System)
# Your name: Tiffany Phoebe Sudijono
# Your student id: 53069112
# Your email: tsudijon@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT): I worked on this project independently, and did not use any form of Gen AI to complete the assignment.
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    results = []

    if not os.path.isabs(html_path):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        html_path = os.path.join(base_dir, html_path)

    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")

    listing_links = soup.find_all("a", href=True)
    for link in listing_links:
        href = link['href']
        if "/rooms/" in href:
            match = re.search(r'/rooms/(?:plus/)?(\d+)', href)
            if not match:
                continue
            listing_id = match.group(1)
            title_tag = soup.find(id=f"title_{listing_id}")
            listing_title = title_tag.get_text().strip() if title_tag else "No Title"
            if (listing_title, listing_id) not in results:
                results.append((listing_title, listing_id))

    return results
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    base_dir = os.path.abspath(os.path.dirname(__file__))
    html_path = os.path.join(base_dir, "html_files", f"listing_{listing_id}.html")

    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Extract policy number
    policy_tag = soup.find(string=re.compile(r"STR|Pending|Exempt"))
    policy_text = policy_tag.strip() if policy_tag else "Pending"
    match = re.search(r"(\d{4}-\d+STR|STR-\d+)", policy_text)
    policy_number = match.group(0) if match else policy_text

    # Determine host type
    host_type_tag = soup.find("span", string=re.compile("Superhost"))
    host_type = "Superhost" if host_type_tag else "regular"

    # Extract host name
    host_name_tag = soup.find("h2", string=re.compile("Hosted by"))
    if host_name_tag:
        host_name = host_name_tag.get_text().replace("Entire loft hosted by", "").replace("Hosted by", "").strip()
    else:
        host_name = "Unknown"

    # Determine room type from subtitle
    subtitle_tag = soup.find("div", class_="_1jlr81g")
    subtitle_text = subtitle_tag.get_text() if subtitle_tag else ""
    if "Private" in subtitle_text:
        room_type = "Private Room"
    elif "Shared" in subtitle_text:
        room_type = "Shared Room"
    else:
        room_type = "Entire Room"

    # Extract location rating
    location_rating = 0.0
    label_divs = soup.find_all("div", class_="_y1ba89")
    for div in label_divs:
        if div.get_text().strip() == "Location":
            next_div = div.find_next_sibling("div")
            if next_div:
                try:
                    location_rating = float(next_div.get_text().strip())
                except:
                    location_rating = 0.0
            break

    # Build the nested dictionary
    details = {
        listing_id: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating
        }
    }

    return details
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    database = []

    listings = load_listing_results(html_path)

    for listing_title, listing_id in listings:
        details_dict = get_listing_details(listing_id)

        if listing_id in details_dict:
            info = details_dict[listing_id]

            listing_tuple = (
                listing_title,
                listing_id,
                info.get("policy_number", "Pending"),
                info.get("host_type", "regular"),
                info.get("host_name", "Unknown"),
                info.get("room_type", "Entire Room"),
                info.get("location_rating", 0.0)
            )

            database.append(listing_tuple)

    return database
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    sorted_data = sorted(data, key=lambda x: x[6], reverse=True)

    headers = ["Listing Title", "Listing ID", "Policy Number", "Host Type", "Host Name", "Room Type", "Location Rating"]

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in sorted_data:
            writer.writerow(row)
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    ratings = {}

    for listing in data:
        room_type = listing[5]
        rating = listing[6]

        if rating == 0.0:
            continue

        if room_type not in ratings:
            ratings[room_type] = [rating]
        else:
            ratings[room_type].append(rating)

    avg_ratings = {}
    for room_type, rating_list in ratings.items():
        avg_ratings[room_type] = round(sum(rating_list) / len(rating_list), 2)

    return avg_ratings
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    invalid_listings = []

    pattern1 = r"20\d{2}-00\d{4}STR"  # 20##-00####STR
    pattern2 = r"STR-000\d{4}"        # STR-000####

    for listing in data:
        listing_id = listing[1]
        policy_number = listing[2]

        if policy_number in ["Pending", "Exempt"]:
            continue

        if not (re.fullmatch(pattern1, policy_number) or re.fullmatch(pattern2, policy_number)):
            invalid_listings.append(listing_id)

    return invalid_listings
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    query = query.replace(" ", "+")
    url = f"https://scholar.google.com/scholar?q={query}"

    # Headers to mimic a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/100.0.4896.127 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch Google Scholar page")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    titles = []
    # Google Scholar titles are usually in h3 with class 'gs_rt'
    for h3 in soup.find_all("h3", class_="gs_rt"):
        # Remove extra tags like <a> or <span> inside
        title_text = h3.get_text().strip()
        if title_text:
            titles.append(title_text)

    return titles
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        self.assertEqual(len(self.listings), 18)
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        results = []
        for listing_id in html_list:
            results.append(get_listing_details(listing_id))

        # 1) policy number check
        self.assertEqual(results[0]["467507"]["policy_number"], "STR-0005349")

        # 2) host type + room type
        self.assertEqual(results[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(results[2]["1944564"]["room_type"], "Entire Room")

        # 3) location rating
        self.assertEqual(results[2]["1944564"]["location_rating"], 4.9)

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        for listing in self.detailed_data:
            self.assertEqual(len(listing), 7)

        self.assertEqual(
            self.detailed_data[-1],
            ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8)
        )

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].
        output_csv(self.detailed_data, out_path)

        rows = []
        with open(out_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)

        self.assertEqual(
            rows[1],
            ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"]
        )

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        result = avg_location_rating_by_room_type(self.detailed_data)
        self.assertEqual(result["Private Room"], 4.9)

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        invalid_listings = validate_policy_numbers(self.detailed_data)
        self.assertEqual(invalid_listings, ["16204265"])

def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")

if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)