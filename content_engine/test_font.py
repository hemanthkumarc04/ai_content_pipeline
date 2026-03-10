from PIL import Image, ImageDraw, ImageFont
import os

def test_kannada_font():
    print("🛠️ Starting Font Diagnostic...")
    
    # Create a small black canvas
    img = Image.new('RGB', (400, 150), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    test_text = "ನಮಸ್ಕಾರ (Namaskara)"
    
    # 1. Try relative path (how the main app calls it)
    try:
        font = ImageFont.truetype("nirmala.ttf", 40)
        print("✅ SUCCESS: Found 'nirmala.ttf' in system PATH.")
    except Exception as e:
        print(f"⚠️ FAILED relative path: {e}")
        # 2. Try absolute Windows path
        try:
            hard_path = r"C:\Windows\Fonts\nirmala.ttf"
            font = ImageFont.truetype(hard_path, 40)
            print(f"✅ SUCCESS: Found font using absolute path: {hard_path}")
        except Exception as e2:
            print(f"❌ FATAL ERROR: Cannot find Nirmala UI font at all. {e2}")
            return

    # Draw the text in yellow
    draw.text((20, 40), test_text, font=font, fill=(255, 255, 0))
    
    # Save the output
    output_file = "diagnostic_kannada_test.png"
    img.save(output_file)
    print(f"🖼️ Diagnostic image saved as '{output_file}'.")
    print("👉 OPEN THE IMAGE NOW. If you see boxes instead of Kannada, your system doesn't support the script.")

if __name__ == "__main__":
    test_kannada_font()