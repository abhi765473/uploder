import requests
import sys

# Set the console to use UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

def course_details(token2, institute_name, org_code):
    # URL for the API with the token included
    url = f"https://api.classplusapp.com/v2/course/preview/similar/{token2}?filterId=[1]&sortId=[7]&subCatList=&mainCategory=0&limit=1000&offset="

    # Make a GET request to the API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Get the JSON data from the response
        data = response.json()
        # Extract and print only the IDs and names with a nice design
        courses = data.get('data', {}).get('coursesData', [])
        # Create a file name based on the institute name and org code
        file_name = f"{institute_name}_{org_code}_courses.txt"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(f"Institute Name= {institute_name}\n")
            file.write("-" * 40 + "\n")
            file.write(f"Org Code = {org_code}\n")
            file.write("Course IDs and Names:\n")
            file.write("-" * 40 + "\n")
            for idx, course in enumerate(courses, start=1):
                price = course.get('price')
                price_str = f"₹{price:,.2f}" if price is not None else "N/A"
                file.write(f"{idx:<5} | {course.get('id'):<10} | {course.get('name'):<50} | {price_str}\n")
                file.write("-" * 40 + "\n")
        print(f"Course details have been saved to {file_name}")
    else:
        print(f"Request failed with status code {response.status_code}")

@bot.on_message(filters.command("app") & filters.private)
async def fetch_courses_command(client, msg):
    chat_id = msg.chat.id

    # Step 1: Ask for the token
    if chat_id not in user_inputs:
        user_inputs[chat_id] = {}
        await msg.reply("Enter your token:")
        token_msg = await bot.listen(chat_id)
        user_inputs[chat_id]["token2"] = token_msg.text
        await msg.reply("Enter your institute name:")
        institute_name_msg = await bot.listen(chat_id)
        user_inputs[chat_id]["institute_name"] = institute_name_msg.text
        await msg.reply("Enter your org code:")
        org_code_msg = await bot.listen(chat_id)
        user_inputs[chat_id]["org_code"] = org_code_msg.text

        token2 = user_inputs[chat_id]["token2"]
        institute_name = user_inputs[chat_id]["institute_name"]
        org_code = user_inputs[chat_id]["org_code"]

        course_details(token2, institute_name, org_code)

        del user_inputs[chat_id]  # Clear user inputs after processing

        await msg.reply(f"Course details have been fetched and saved to {institute_name}_{org_code}_courses.txt.")
        return
