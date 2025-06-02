import streamlit as st
import pefile
from PIL import Image
from io import BytesIO

st.title("🎮 EO Sprite Viewer")
st.markdown("**How it works:** EO hides sprites inside fake .exe files. We dig them out!")

# User inputs
gfx_file = st.number_input("GFX File (like gfx002.egf)", 1, 999, 2)
sprite_num = st.number_input("Sprite ID (sprite 1, 2, 3...)", 1, 999, 1)

if st.button("🔍 Extract Sprite"):
    with st.spinner("Digging through the file..."):
        try:
            # STEP 1: Build the file path to the EGF file
            file_path = rf"./gfx/gfx{gfx_file:03d}.egf"
            st.info(f"📁 **Step 1:** Looking for file: `gfx{gfx_file:03d}.egf`")
            
            # STEP 2: Open the disguised executable file
            graphics_file = pefile.PE(file_path)
            st.info(f"🔓 **Step 2:** Opened the fake .exe file (it's really a graphics container)")
            
            # STEP 3: Navigate to the hidden images section
            st.info(f"🗂️ **Step 3:** Searching for the 'bitmap resources' section...")
            found_sprite = False
            
            for resource_type in graphics_file.DIRECTORY_ENTRY_RESOURCE.entries:
                if resource_type.id == 2:  # ID 2 = bitmap type in Windows PE files
                    st.info(f"✅ **Step 4:** Found the images section! Looking for sprite {sprite_num}...")
                    
                    # STEP 4: Find our specific sprite
                    for sprite_entry in resource_type.directory.entries:
                        if sprite_entry.id == sprite_num + 100:  # EO's weird numbering: sprite 1 = ID 101
                            st.info(f"🎯 **Step 5:** Found sprite {sprite_num} (stored as resource ID {sprite_num + 100})")
                            
                            # STEP 5: Get the memory location where sprite data is stored
                            sprite_data_location = sprite_entry.directory.entries[0].data.struct.OffsetToData
                            sprite_data_size = sprite_entry.directory.entries[0].data.struct.Size
                            st.info(f"📍 **Step 6:** Sprite is at position {sprite_data_location}, size {sprite_data_size} bytes")
                            
                            # STEP 6: Extract the raw image bytes
                            sprite_bytes = graphics_file.get_data(sprite_data_location, sprite_data_size)
                            st.info(f"💾 **Step 7:** Extracted {len(sprite_bytes)} bytes of raw image data")
                            
                            # STEP 7: Convert raw bytes back into a viewable image
                            sprite_image = Image.open(BytesIO(sprite_bytes))
                            st.info(f"🖼️ **Step 8:** Converted bytes to {sprite_image.width}x{sprite_image.height} pixel image")
                            
                            # STEP 8: Display the final result
                            st.success(f"🎉 **Step 9:** Success! Here's your sprite:")
                            st.image(sprite_image, caption=f"Sprite {sprite_num} from gfx{gfx_file:03d}.egf ({sprite_image.width}x{sprite_image.height})")
                            
                            found_sprite = True
                            break
                    
                    if not found_sprite:
                        st.error(f"❌ Sprite {sprite_num} not found in this file (looked for resource ID {sprite_num + 100})")
                    break
            else:
                st.error("❌ No image section found in this file (not a valid EGF file?)")
                
        except FileNotFoundError:
            st.error(f"❌ File not found: `gfx{gfx_file:03d}.egf`")
        except Exception as error:
            st.error(f"❌ Something went wrong: {error}")

st.markdown("---")
st.markdown("""
**🤔 Why is this so complicated?**
- Normal images: Just open `sprite.png` ✅
- EO images: Hidden inside fake Windows executable files 🤯
- We have to pretend to be Windows and parse the .exe format to find the pictures!

**💡 Fun fact:** EGF files are actually Windows .exe files with pictures stuffed inside them instead of code.
""")

st.caption("Enter a GFX file number (1-999) and sprite number (1-999), then click 'Extract Sprite'")