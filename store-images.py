from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS
import os, dotenv
import shutil
import sqlite3
#import fitz  # PyMuPDF for image extraction
    #import pymupdf
    # or
import pymupdf as fitz
import io
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import time

load_dotenv()

#os.environ['OPNEAI_API_KEY'] = "API-KEY"
os.environ['OPENAI_API_KEY'] = "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"
client = OpenAI()
# Define paths
DATA_PATHS = [
    ["./Data/20200910_ON_POINT_SERVICE_Manual_En_2CA123513967E.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/250/20200910_ON_POINT_SERVICE_Manual_En_2CA123513967E.pdf"],
    ["./Data/A120__Addams_Family_LCD_GMP_Manual__4FA5B5C3C573D.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/413/A120__Addams_Family_LCD_GMP_Manual__4FA5B5C3C573D.pdf"],
    ["./Data/bean bag toss Rev Q 4-25-2024.pdf", "https://www.dropbox.com/scl/fo/8pdasz3v7mqhx93dv6bkr/AOCD0ZW_0ESc0YNlnLRpVkU?dl=0&e=1&preview=bean+bag+toss+Rev+Q+4-25-2024.pdf&rlkey=t21r6n0e2y75yi7nmyyv7ixwz&st=h28tecoh"],
    ["./Data/big_bass_wheel.pdf", "https://www.manualslib.com/manual/1352315/Bay-Tek-Games-Big-Bass-Wheel.html"],
    ["./Data/Godzilla_Kaiju_Wars_VR_Manual.pdf", "https://drive.google.com/file/d/1wn0uqOyg2Cf2OotvXEJ9A7osGBuyXsey/view"],
    ["./Data/ICEBALL FX rev R 1-23-25.pdf", "https://www.dropbox.com/scl/fo/shqiv1reglc1rtgoxfvjj/AJMm-Bwyl7G12OkLMcOIgk8?dl=0&e=1&preview=ICEBALL+FX+rev+R+1-23-25.pdf&rlkey=r79naavebsvwi3xlu0d4bbn4d&st=3xd2e3wu"],
    ["./Data/squiggle.pdf", "https://www.manualslib.com/manual/1824374/Baytek-Games-Squiggle.html"],
]

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(CURRENT_DIR, "db", "updated-db")
IMAGE_DB_PATH = os.path.join(CURRENT_DIR, "db", "images.db")

def initialize_database():
    """Initialize SQLite database with proper permissions"""
    try:
        # Ensure directory exists
        db_dir = os.path.dirname(IMAGE_DB_PATH)
        os.makedirs(db_dir, exist_ok=True)
        
        # Set directory permissions (777 for development, adjust for production)
        os.chmod(db_dir, 0o777)
        
        # If database exists, set proper permissions
        if os.path.exists(IMAGE_DB_PATH):
            os.chmod(IMAGE_DB_PATH, 0o666)
        else:
            # Create new database file with proper permissions
            open(IMAGE_DB_PATH, 'a').close()
            os.chmod(IMAGE_DB_PATH, 0o666)
        
        # Create database connection
        conn = sqlite3.connect(IMAGE_DB_PATH)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pdf_name TEXT,
                page_num INTEGER,
                image BLOB,
                pdf_link TEXT
            )
        """)
        conn.commit()
        return conn, cursor
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        if 'conn' in locals():
            conn.close()
        raise

print(f"Current directory: {CURRENT_DIR}")
print(f"Database directory path: {DATABASE_DIR}")


import fitz  # PyMuPDF
import os
import base64

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')



def pageDescription(manual_name, page, image):
    base64_image = encode_image(image)
    response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {
          "role": "user",
          "content": [
            {"type": "text", "text": f'''
                This is a page about the manual from {manual_name}, at page {page}. Give me a description of the page so that I may retrieve it from a vector database efficiently later. Your response must include the games name, the page number, and a description of the contents of the page.
               '''},
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "high"
              },
            },
          ],
        }
      ],
      max_tokens=4096,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content





def pdf_to_pngs(pdf_path, cleanName, output_folder="output", dpi=300):
    try:
        # Open the PDF
        pdf_document = fitz.open(pdf_path[0])
        pages = []
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Convert each page to PNG with a white background
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), colorspace=fitz.csRGB)  # Set resolution
            pix.save(os.path.join(output_folder, f"{cleanName}_page_{page_num+1}.png"))
            pngpath = os.path.join(output_folder, f"{cleanName}_page_{page_num+1}.png")
            print(f"Saved {os.path.join(output_folder, f'{cleanName}_page_{page_num+1}.png')}")
            pages.append(pngpath)
        
        pdf_document.close()
        return pages
    
    except Exception as e:
        return f"Error: {str(e)}"


def cleanText(filename):
 completion = client.chat.completions.create(
   model="gpt-4o-mini",
   messages=[
     {"role": "system", "content": "You are text cleaner agent. You take the name of a file and clean it so the returned text only has the name of the game and the and term 'Manual'. Exclude all other random characters and numbers in the return text."},
     {"role": "user", "content": "Godzilla_Kaiju_Wars_VR_Manual.pdf"},
     {"role": "assistant", "content": "Godzilla Kaiju Wars VR Manual"},
     {"role": "user", "content": "20200910_ON_POINT_SERVICE_Manual_En_2CA123513967E.pdf"},
     {"role": "assistant", "content": "On Point Service Manual"},
     {"role": "user", "content": f"{filename}"},
   ]
 )
 result = completion.choices[0].message.content
 print(completion.choices[0].message.content)
 return result

def image_to_bytes(image_path):
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Convert to RGB if it's in a different mode (e.g., RGBA)
            img = img.convert("RGB")
            # Create a bytes buffer
            byte_io = io.BytesIO()
            # Save the image to the buffer in PNG format
            img.save(byte_io, format="PNG")
            # Get the byte data
            byte_data = byte_io.getvalue()
            return byte_data
    except Exception as e:
        return f"Error: {str(e)}"

# # Connect to SQLite and create image table
# with sqlite3.connect(IMAGE_DB_PATH) as conn:
    # cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS images (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             pdf_name TEXT,
#             page_num INTEGER,
#             image BLOB,
#             pdf_link TEXT
#             )
#     """)
    # conn.commit()



def store_images_from_pdf(pdf_path, cleanName):
    """Extracts and stores images from a PDF into SQLite."""
    print("STORING IMAGES FROM PDF")
    doc = fitz.open(pdf_path[0])
    pdf_name = os.path.basename(pdf_path[0])
    pages = pdf_to_pngs(pdf_path, cleanName)
    
    conn = None
    conn, cursor = initialize_database()
    #for index, page_num in enumerate(range(len(doc))):
    for index, page in enumerate(pages):
            link = pdf_path[1]
            # NEED TO ADD DESCRIPTION of page
        #for img in doc[page_num].get_images(full=True):
            #print(f" the current page of the document is - {img}, xref is {img[0]}")
            #xref = img[0]
            #base_image = doc.extract_image(xref)
            #image_bytes = base_image["image"]
            image_bytes = image_to_bytes(pages[index])
            page_num = index
            print(f"INSERT INTO images pdf_name {pdf_name}, page_num {index}, image ")
            cursor.execute("INSERT INTO images (pdf_name, page_num, image, pdf_link) VALUES (?, ?, ?, ?)",
                           (cleanName, page_num, image_bytes, link))
            conn.commit()

def create_vector_store():
    print(f"""Creates a FAISS vector database from the given PDF documents.""")
    try:
        print("Creating vector store...")
        os.makedirs(DATABASE_DIR, exist_ok=True)

        documents = []
        for pdf_path in DATA_PATHS:
            print(f"CURRENT PDF PATH IS {pdf_path[0]}")
            loader = PyPDFLoader(pdf_path[0])
            docs = loader.load()
            cleanName = cleanText(os.path.basename(pdf_path[0]))
            print(f"ABOUT TO LOOP THROUGH DOCS IN {cleanName}")
            time.sleep(5)
            # Add metadata (file name & page number)
            for doc in docs:
                doc.metadata["source"] = cleanName
                #os.path.basename(pdf_path)  # Store filename
                doc.metadata["page"] = doc.metadata.get("page", "N/A")  # Store page number
                

            documents.extend(docs)
            #store_images_from_pdf(pdf_path)
            store_images_from_pdf(pdf_path, cleanName)  # Extract and store images

        # Split the documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        split_docs = text_splitter.split_documents(documents)

        # Add more specific page range information to each chunk
        for doc in split_docs:
            doc.metadata["page_start"] = doc.metadata.get("page", 0)
            doc.metadata["page_end"] = doc.metadata.get("page", 0)

        # Create vector store
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large",)
        vector_store = FAISS.from_documents(split_docs, embedding=embeddings)
        print(f"About to save vector store to: {DATABASE_DIR}")
        vector_store.save_local(DATABASE_DIR)

        print("✅ Vector store and image storage completed successfully!")
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")

interactive = os.environ.get("INTERACTIVE_MODE", "true").lower() == "true"
# Main execution logic
if __name__ == "__main__":
    if not os.path.exists(DATABASE_DIR):
        print("Database does not exist. Initializing vector store...")
        create_vector_store()
    else:
        if interactive:
            user_input = input("Vector store already exists. Do you want to recreate the vector database? (yes/no): ").strip().lower()
            if user_input == "yes":
                shutil.rmtree(DATABASE_DIR)
                if os.path.exists(IMAGE_DB_PATH):
                    os.remove(IMAGE_DB_PATH)
                create_vector_store()
            else:
                print("Using existing vector store.")
        else:
           shutil.rmtree(DATABASE_DIR)
           if os.path.exists(IMAGE_DB_PATH):
                os.remove(IMAGE_DB_PATH)
                create_vector_store()

# Close SQLite connection
#conn.close()
