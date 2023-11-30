from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

import os
@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=300,
    )
    download_csv_file()
    open_robot_order_website()
    orders = get_orders()
    for order in orders:
        close_annoying_modal()
        screenshot_filepath = fill_form_for_one_order(order)
        pdf_filepath = store_receipt_as_pdf(order)
        embed_screenshot_to_receipt(screenshot_filepath, pdf_filepath, order)
        order_another_robot()
    archive_receipts()

def download_csv_file():
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)
    
def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    
def get_orders():
    library = Tables()
    orders = library.read_table_from_csv(
    "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
)
    return orders
    
def close_annoying_modal():
    page = browser.page()
    page.click('//button[@class="btn btn-dark"]')
            
def fill_form_for_one_order(order):
    page = browser.page()
    page.select_option('#head', order['Head'])
    radio_button_locator = '#id-body-' + order['Body']
    page.click(radio_button_locator)
    page.fill('//input[@type="number"]', order['Legs'])
    page.fill('#address', order['Address'])
    page.click('#preview')
    robot_preview = page.query_selector('#robot-preview-image')
    screenshot_filepath = "output/" + order['Order number'] + ".png"
    robot_preview.screenshot(path=screenshot_filepath)
    error = '//div[@class="alert alert-danger"]'
    while True:
        page.click('#order')
        if not page.is_visible(error):
            break
    return screenshot_filepath

def store_receipt_as_pdf(order):
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_filepath = "output/" + order['Order number'] +  ".pdf"
    pdf.html_to_pdf(receipt_html, pdf_filepath)
    return pdf_filepath

def embed_screenshot_to_receipt(screenshot_filepath, pdf_filepath, order):
    pdf = PDF()
    list_of_files = [
        pdf_filepath,
        screenshot_filepath
    ]
    output_dir = "output/receipts"
    new_pdf_filepath = os.path.join(output_dir, order['Order number'] + ".pdf")
    # Check if the directory exists, and create it if it doesn't
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pdf.add_files_to_pdf(
        files=list_of_files,
        target_document = new_pdf_filepath,
        append = True
    )

def order_another_robot():
    page = browser.page()
    page.click("#order-another")

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("output/receipts", "output/Receipts.zip")