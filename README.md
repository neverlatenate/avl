# Asheville Jewish Heritage Walking Tour Map

This is the code and assets for the **Asheville Jewish Heritage Walking Tour Map**, featuring a custom Google Maps integration, dynamic stop filtering, dynamic dark mode styling, and full mobile compatibility.

## How to Make this Website Live on GitHub (GitHub Pages)

You can publish this website for free using **GitHub Pages**. Below are two ways to do this:

### Option A: Using the GitHub Web Interface (Easiest - No command line required!)

1. **Sign in to GitHub**: Go to [github.com](https://github.com/) and log in (or create a free account).
2. **Create a New Repository**:
   - Click the **"+"** icon in the top-right corner and select **New repository**.
   - Set the repository name to: `asheville-jewish-heritage-tour` (or any name you like).
   - Keep it **Public** (required for free GitHub Pages).
   - **Do NOT** check the box for "Add a README file" (as we already have this README file in the folder).
   - Click **Create repository**.
3. **Upload the Files**:
   - On the quick setup page, click the link that says **"uploading an existing file"** (near the top).
   - Drag and drop **all files and folders** from this folder (`asheville-jewish-heritage-tour`) into the drag-and-drop area.
   - *Note*: Ensure `index.html` and the images (`.jpg` and `.png`) are uploaded to the main root level, and the `src` folder is uploaded as a subfolder.
   - Wait for the files to finish loading, scroll to the bottom, and click **Commit changes**.
4. **Enable GitHub Pages**:
   - In your repository, click the **Settings** tab (the gear icon at the top).
   - On the left sidebar, click **Pages** (under the "Code and automation" section).
   - Under **Build and deployment** -> **Source**, select **Deploy from a branch**.
   - Under **Branch**, change **None** to **main**, keep the folder as `/ (root)`, and click **Save**.
5. **Visit Your Live Map**:
   - Wait about 1 to 2 minutes.
   - Refresh the page. You will see a banner at the top of the Pages settings page showing your live URL (usually `https://yourusername.github.io/asheville-jewish-heritage-tour/`). Click it to view your live walking tour!

---

### Option B: Using the Command Line (For Git Users)

If you have `git` installed on your Mac, you can run these commands in your Terminal:

1. Open **Terminal** and navigate to the project directory:
   ```bash
   cd "/Users/nateschulman/Desktop/asheville-jewish-heritage-tour"
   ```
2. Initialize Git, stage, and commit the files:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Mobile compatible walking tour map"
   ```
3. Create your repository on GitHub first, then link and push:
   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/asheville-jewish-heritage-tour.git
   git push -u origin main
   ```
4. Follow **Step 4** from Option A to enable **GitHub Pages** in the repository settings on GitHub.

---

## File Structure

```text
asheville-jewish-heritage-tour/
├── index.html                       # The compiled, live walking tour webpage
├── *.jpg, *.png                     # Image assets for the stops
├── README.md                        # This instruction manual
└── src/                             # Source code & build tools
    ├── avl.csv                      # Stop text, addresses, questions, and image list
    ├── build_asheville.py           # Python compiler that generates index.html
    ├── geocoded_avl.json            # Geocode cache of lat/lng coordinates
    ├── geocode.py                   # Geocoder helper
    ├── geocode_output.json          # Raw geocode outputs
    └── map.html                     # Backup html template
```

## How to Update the Map Content in the Future

If you want to add new stops, edit descriptions, change answers, or replace images:

1. Open `src/avl.csv` in a spreadsheet editor (like Excel or Google Sheets) or a text editor.
2. Edit the columns (such as `Landmark`, `Address`, `TeachingPoint`, `Question`, `Answer`, `Image`).
   - *Note*: If you add a new image file, place the `.jpg` or `.png` file in the root folder of the project. If a stop has multiple images, separate their filenames with a comma in the `Image` column.
3. Open your terminal and run the build script:
   ```bash
   cd "/Users/nateschulman/Desktop/asheville-jewish-heritage-tour/src"
   python3 build_asheville.py
   ```
4. This script will automatically:
   - Geocode any new addresses you added.
   - Regenerate the updated `index.html` at the root.
5. Push or drag-and-drop the newly generated `index.html` (and any new images) to your GitHub repository to update your live website instantly!
