import base64
import os
from pathlib import Path
from typing import Dict, Optional
import json
import re

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Configuration des couleurs de rouge à lèvres avec leurs codes hex
LIPSTICK_COLORS = {
    'Ruby': '#932432',
    'Terracotta': '#B85C3C',
    'Dusty Rose': '#C48B99',
    'Natural Nude': '#BE8B7B',
    'Berry Wine': '#6E2F3D',
    'Soft Coral': '#DB8075'
}

class LipstickAnalyzer:
    def __init__(self):
        # load_dotenv()
        # self.api_key = os.getenv("OPENAI_API_KEY")
        # self.client = OpenAI()
        self.api_key = st.secrets["OPENAI_API_KEY"]
        self.client = OpenAI()

    def _encode_image(self, image_bytes: bytes) -> str:
        return base64.b64encode(image_bytes).decode("utf-8")

    def _clean_response(self, response: str) -> Dict:
        # Supprimer les balises code et json
        cleaned = re.sub(r'```json\s*|\s*```', '', response)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "chosen_color": "Ruby",
                "analysis": "Désolé, une erreur s'est produite pendant l'analyse."
            }

    def analyze_image(self, image_bytes: bytes) -> Optional[Dict]:
        try:
            base64_image = self._encode_image(image_bytes)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es une conseillère beauté experte et amicale. Tu dois analyser les photos et suggérer le meilleur rouge à lèvres. Ta réponse doit TOUJOURS être en JSON valide."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyse cette photo et suggère la meilleure teinte de rouge à lèvres parmi ces options uniquement:
                                - Ruby (rouge classique)
                                - Terracotta (orangé nude)
                                - Dusty Rose (rose naturel)
                                - Natural Nude (beige naturel)
                                - Berry Wine (prune foncé)
                                - Soft Coral (corail doux)
                                
                                Tu DOIS répondre EXACTEMENT dans ce format JSON :
                                {"chosen_color": "EXACTEMENT UN DES NOMS CI-DESSUS", "analysis": "Ton analyse friendly en français qui commence par Hey beauty! ou Coucou beauté!"}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=150
            )
            
            response_content = response.choices[0].message.content
            return self._clean_response(response_content)
            
        except Exception as e:
            st.error(f"Erreur d'analyse: {str(e)}")
            return {
                "chosen_color": "Ruby",
                "analysis": "Désolé, une erreur s'est produite pendant l'analyse. Veuillez réessayer."
            }

def main():
    st.set_page_config(
        page_title="Analyse Rouge à Lèvres",
        page_icon="💄",
        layout="wide"
    )

    # CSS personnalisé amélioré
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Roboto:wght@300;400;500&display=swap');
        
        .stApp {
            background-color: #fdf4ff;
            font-family: 'Roboto', sans-serif;
        }
        div[data-testid="stFileUploader"] {
            border: 2px dashed #d946ef;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
        }
        div[data-testid="stFileUploader"]:hover {
            border-color: #a21caf;
            box-shadow: 0 0 10px rgba(217, 70, 239, 0.2);
        }
        .stButton > button {
            background-color: #a21caf;
            color: white;
            border-radius: 30px;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            border: none;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #86198f;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .main-title {
            font-family: 'Playfair Display', serif;
            color: #701a75;
            font-size: 2.5rem;
            margin-bottom: 2rem;
            text-align: center;
            font-weight: 700;
        }
        .color-box {
            width: 100%;
            height: 150px;
            border-radius: 12px;
            margin-bottom: 0.5rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .color-box:hover {
            transform: scale(1.05);
        }
        .selected-badge {
            background-color: #a21caf;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            display: inline-block;
            margin-top: 0.5rem;
            font-weight: 500;
        }
        .analysis-title {
            font-family: 'Playfair Display', serif;
            color: #701a75;
            font-size: 1.8rem;
            margin: 2rem 0 1rem 0;
            text-align: center;
        }
        .analysis-text {
            background-color: #fae8ff;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            line-height: 1.6;
            font-size: 1.1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 2px solid #d946ef;
        }
        .final-choice {
            display: flex;
            align-items: center;
            margin-top: 2rem;
            gap: 12px;
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .color-indicator {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: inline-block;
            vertical-align: middle;
            border: 2px solid white;
            box-shadow: 0 0 0 2px #a21caf;
        }
        .style-id {
            background-color: #fae8ff;
            padding: 1rem;
            border-radius: 12px;
            margin: 1rem 0;
            color: #701a75;
            font-weight: 500;
            text-align: center;
            font-size: 1.2rem;
            letter-spacing: 1px;
        }
        .color-name {
            font-weight: 500;
            margin-top: 0.5rem;
            font-size: 1.1rem;
        }
        .selected-color-box {
            border: 3px solid #a21caf;
            position: relative;
        }
        .selected-color-box::after {
            content: 'Sélectionné';
            position: absolute;
            top: -10px;
            right: 10px;
            background-color: #a21caf;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        .uploaded-image {
            border: 4px solid #d946ef;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Layout principal
    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.markdown('<h1 class="main-title">Votre Analyse Beauté Personnalisée</h1>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Déposez votre photo ici pour une analyse sur mesure",
            type=['png', 'jpg', 'jpeg'],
            help="Limite 200MB par fichier • PNG, JPG, JPEG"
        )

        if uploaded_file:
            st.markdown(f'<img src="data:image/jpeg;base64,{base64.b64encode(uploaded_file.getvalue()).decode()}" class="uploaded-image" style="width:100%">', unsafe_allow_html=True)
            
            st.markdown('<div class="style-id">Style ID: LOOK_001</div>', 
                       unsafe_allow_html=True)
            
            if st.button("Révélez Votre Teinte Parfaite"):
                with right_col:
                    st.markdown('<h1 class="main-title">Votre Palette Personnalisée</h1>', 
                              unsafe_allow_html=True)
                    
                    analyzer = LipstickAnalyzer()
                    result = analyzer.analyze_image(uploaded_file.getvalue())
                    
                    if result:
                        chosen_color = result["chosen_color"]
                        
                        # Grille des couleurs améliorée
                        col1, col2, col3 = st.columns(3)
                        cols = [col1, col2, col3]
                        for idx, (name, color) in enumerate(LIPSTICK_COLORS.items()):
                            with cols[idx % 3]:
                                st.markdown(f"""
                                    <div style="text-align: center;">
                                        <div class="color-box {'selected-color-box' if name == chosen_color else ''}" 
                                             style="background-color: {color};">
                                        </div>
                                        <div class="color-name">{name}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        # Détails de l'analyse
                        st.markdown('<h2 class="analysis-title">Votre Analyse Beauté Exclusive</h2>', 
                                  unsafe_allow_html=True)
                        
                        # Affichage de l'analyse sans formatage JSON
                        st.markdown(f'<div class="analysis-text">{result["analysis"]}</div>', 
                                  unsafe_allow_html=True)
                        
                        # Choix final
                        st.markdown(f"""
                            <div class="final-choice">
                                <div class="color-indicator" 
                                     style="background-color: {LIPSTICK_COLORS[chosen_color]};">
                                </div>
                                <strong>Votre Teinte Idéale:</strong> {chosen_color}
                            </div>
                        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()