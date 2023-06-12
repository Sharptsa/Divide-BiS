import streamlit as st
import streamlit.components.v1 as components

# Title and text box
wowhead_js_script1 = '<script>const whTooltips = {colorLinks: true, iconizeLinks: true, renameLinks: true};</script>'
wowhead_js_script2 = '<script src="https://wow.zamimg.com/js/tooltips.js"></script>'
# html(wowhead_js_script)
st.title('Temp title')
components.html(wowhead_js_script2)
# st.markdown(wowhead_js_script1, unsafe_allow_html=True)
# st.markdown(wowhead_js_script2, unsafe_allow_html=True)
st.markdown('<a href="#" data-wowhead="item=100244"> some_item_link2</a>', unsafe_allow_html=True)