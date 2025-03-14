import base64
import os
from pathlib import Path
from typing import Dict, Optional
import json
import re

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Configuration des types de barbe avec leurs descriptions
BEARD_STYLES = {
    'Barbe Complète': 'Une barbe épaisse et complète qui couvre tout le visage',
    'Barbe Courte': 'Style entretenu et court, parfait pour un look professionnel',
    'Bouc': 'Barbe au menton avec moustache, sans poils sur les joues',
    'Barbe de 3 Jours': 'Look légèrement négligé qui convient à de nombreux visages',
    'Moustache': 'Focus sur la moustache, parfait pour un style distinctif',
    'Collier': 'Barbe qui suit la ligne de la mâchoire sans moustache'
}

# Couleurs recommandées pour la barbe
BEARD_COLORS = {
    'Naturel': 'Gardez votre couleur naturelle',
    'Noir': 'Teinte noire profonde',
    'Brun Foncé': 'Couleur brune riche',
    'Brun Clair': 'Teinte brune plus claire',
    'Roux': 'Teinte rousse chaude',
    'Gris/Poivre et Sel': 'Effet naturel de vieillissement élégant'
}

# Produits L'Oréal recommandés pour l'entretien de la barbe
LOREAL_PRODUCTS = {
    'Coloration': {
        'L\'Oréal Paris Barbe Longue': 'Coloration permanente spécifique pour barbes longues',
        'L\'Oréal Men Expert BarberClub': 'Gel de précision anti-poils blancs',
        'L\'Oréal Men Expert One-Twist': 'Application facile pour barbes courtes à moyennes'
    },
    'Entretien': {
        'L\'Oréal Men Expert Barber Club Huile': 'Huile nourrissante pour barbe et visage',
        'L\'Oréal Men Expert Barber Club Baume': 'Hydratation intense pour barbes sèches',
        'L\'Oréal Men Expert Barber Club Gel': 'Gel lavant 3-en-1 pour barbe, visage et cheveux'
    },
    'Coiffage': {
        'L\'Oréal Men Expert Barber Club Cire': 'Définition et maintien pour styles structurés',
        'L\'Oréal Men Expert Styling Spray': 'Fixation légère pour barbes et moustaches',
        'L\'Oréal Men Expert Barber Club Gel Coiffant': 'Pour dompter les barbes rebelles'
    }
}

class BeardAnalyzer:
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
                "recommended_style": "Barbe Courte",
                "recommended_color": "Naturel",
                "trim_length_mm": "5-10",
                "has_gray": False,
                "recommendations": {
                    "trim": "Une légère taille est recommandée pour maintenir une apparence professionnelle",
                    "products": ["L'Oréal Men Expert Barber Club Huile", "L'Oréal Men Expert Barber Club Gel"],
                    "routine": "Lavage quotidien et hydratation recommandés"
                },
                "face_shape": "Ovale",
                "problem_areas": [],
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
                        "content": "Tu es un expert en analyse faciale et stylisme capillaire pour hommes de la marque L'Oréal Paris. Tu dois fournir une analyse professionnelle corporative de barbes et recommander des solutions précises et techniques. Ta réponse doit TOUJOURS être en JSON valide avec le format demandé."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyse cette photo avec précision technique et professionnelle:

                                1. Analyse faciale et pilosité:
                                - Forme du visage (ovale, carré, rond, rectangulaire, triangulaire)
                                - Densité de la barbe (clairsemée, moyenne, dense)
                                - Présence de poils blancs/gris (pourcentage approximatif)
                                - Longueur actuelle en mm approximative
                                - Problèmes spécifiques (zones clairsemées, croissance inégale, irritations)

                                2. Recommandations professionnelles:
                                - Style de barbe le plus adapté parmi:
                                  * Barbe Complète
                                  * Barbe Courte
                                  * Bouc
                                  * Barbe de 3 Jours
                                  * Moustache
                                  * Collier
                                
                                - Couleur idéale parmi:
                                  * Naturel
                                  * Noir
                                  * Brun Foncé
                                  * Brun Clair
                                  * Roux
                                  * Gris/Poivre et Sel
                                
                                3. Recommandations techniques:
                                - Longueur optimale en mm précise
                                - Techniques de taille spécifiques (dégradé, contours nets, etc.)
                                - Produits L'Oréal Paris spécifiquement adaptés (nommer 2-3 produits)
                                - Routine d'entretien quotidienne
                                
                                Tu DOIS répondre EXACTEMENT dans ce format JSON:
                                {
                                  "recommended_style": "UN STYLE PRÉCIS",
                                  "recommended_color": "UNE COULEUR PRÉCISE",
                                  "trim_length_mm": "LONGUEUR EN MM",
                                  "has_gray": boolean,
                                  "face_shape": "FORME DU VISAGE",
                                  "problem_areas": ["PROBLÈME 1", "PROBLÈME 2"],
                                  "recommendations": {
                                    "trim": "CONSEIL TECHNIQUE DE TAILLE PRÉCIS",
                                    "products": ["PRODUIT L'ORÉAL 1", "PRODUIT L'ORÉAL 2", "PRODUIT L'ORÉAL 3"],
                                    "routine": "ROUTINE D'ENTRETIEN PROFESSIONNELLE DÉTAILLÉE"
                                  },
                                  "analysis": "TON ANALYSE PROFESSIONNELLE ET CORPORATIVE DÉTAILLÉE EN FRANÇAIS"
                                }"""
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
                max_tokens=800
            )
            
            response_content = response.choices[0].message.content
            return self._clean_response(response_content)
            
        except Exception as e:
            st.error(f"Erreur d'analyse: {str(e)}")
            return {
                "recommended_style": "Barbe Courte",
                "recommended_color": "Naturel",
                "trim_length_mm": "5-10",
                "has_gray": False,
                "recommendations": {
                    "trim": "Une légère taille est recommandée pour maintenir une apparence professionnelle",
                    "products": ["L'Oréal Men Expert Barber Club Huile", "L'Oréal Men Expert Barber Club Gel"],
                    "routine": "Lavage quotidien et hydratation recommandés"
                },
                "face_shape": "Ovale",
                "problem_areas": [],
                "analysis": "Désolé, une erreur s'est produite pendant l'analyse. Veuillez réessayer."
            }

def main():
    st.set_page_config(
        page_title="BarbExpert - L'Oréal Brandstorm",
        page_icon="✂️",
        layout="wide"
    )

    # CSS personnalisé amélioré - Fond blanc avec encadrés noirs
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@400;700;900&display=swap');
        
        .stApp {
            background-color: #ffffff;
            font-family: 'Montserrat', sans-serif;
            color: #000000;
        }
        div[data-testid="stFileUploader"] {
            border: 3px dashed #000000;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
            background-color: #f8f8f8;
        }
        div[data-testid="stFileUploader"]:hover {
            border-color: #333333;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
        }
        .stButton > button {
            background-color: #000000;
            color: #ffffff;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: all 0.3s ease;
            border: none;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #333333;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        .brand-badge {
            position: absolute;
            top: 10px;
            right: 20px;
            background-color: #000000;
            color: #ffffff;
            padding: 8px 15px;
            border-radius: 5px;
            font-weight: 800;
            font-size: 14px;
            letter-spacing: 1px;
        }
        .main-title {
            font-family: 'Montserrat', sans-serif;
            color: #000000;
            font-size: 3.5rem;
            margin-bottom: 0.5rem;
            text-align: center;
            font-weight: 900;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .tagline {
            font-family: 'Montserrat', sans-serif;
            color: #555555;
            font-size: 1.2rem;
            margin-bottom: 2rem;
            text-align: center;
            font-weight: 500;
            letter-spacing: 1px;
        }
        .style-box {
            width: 100%;
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            border: 3px solid #000000;
        }
        .style-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
        }
        .selected-style-box {
            border: 4px solid #000000;
            background-color: #f0f0f0;
        }
        .selected-badge {
            background-color: #000000;
            color: #ffffff;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            display: inline-block;
            margin-top: 0.5rem;
            font-weight: 800;
            letter-spacing: 1px;
        }
        .analysis-title {
            font-family: 'Montserrat', sans-serif;
            color: #000000;
            font-size: 2rem;
            margin: 2rem 0 1rem 0;
            text-align: center;
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
            position: relative;
            padding-bottom: 10px;
        }
        .analysis-title:after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 4px;
            background-color: #000000;
        }
        .analysis-text {
            background-color: #f8f8f8;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            line-height: 1.6;
            font-size: 1.1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 3px solid #000000;
        }
        .final-choice {
            display: flex;
            flex-direction: column;
            margin-top: 1.5rem;
            gap: 12px;
            background-color: #ffffff;
            padding: 1.8rem;
            border-radius: 15px;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
            border: 3px solid #000000;
            position: relative;
            overflow: hidden;
        }
        .final-choice:before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 8px;
            height: 100%;
            background-color: #000000;
        }
        .style-name {
            font-weight: 800;
            margin-top: 0.5rem;
            font-size: 1.3rem;
            color: #000000;
            text-transform: uppercase;
        }
        .style-desc {
            font-weight: 500;
            font-size: 1rem;
            color: #555555;
            margin-top: 0.25rem;
        }
        .uploaded-image {
            border: 5px solid #000000;
            border-radius: 12px;
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
            margin-bottom: 1.5rem;
        }
        .recommendation-item {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 12px;
            position: relative;
            padding-left: 15px;
        }
        .recommendation-label {
            font-weight: 800;
            color: #000000;
            min-width: 140px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9rem;
        }
        .recommendation-value {
            font-weight: 600;
            color: #333333;
            font-size: 1rem;
        }
        .trim-advice {
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
            font-style: italic;
            border-left: 4px solid #000000;
        }
        .logo-text {
            font-family: 'Montserrat', sans-serif;
            font-weight: 900;
            font-size: 2rem;
            letter-spacing: 3px;
            margin-bottom: 0.5rem;
            text-align: center;
            text-transform: uppercase;
        }
        .logo-accent {
            color: #000000;
            font-weight: 900;
            position: relative;
            display: inline-block;
        }
        .logo-accent:after {
            content: '';
            position: absolute;
            bottom: 5px;
            left: 0;
            width: 100%;
            height: 4px;
            background-color: #000000;
        }
        .section-divider {
            height: 3px;
            background: #000000;
            margin: 2.5rem 0;
            width: 100%;
            position: relative;
        }
        .section-divider:before, .section-divider:after {
            content: '';
            position: absolute;
            width: 10px;
            height: 10px;
            background: #000000;
            border-radius: 50%;
            top: 50%;
            transform: translateY(-50%);
        }
        .section-divider:before {
            left: 0;
        }
        .section-divider:after {
            right: 0;
        }
        .product-item {
            background-color: #f8f8f8;
            border-left: 4px solid #000000;
            padding: 12px 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .product-item:hover {
            transform: translateX(5px);
            background-color: #f0f0f0;
        }
        .routine-text {
            line-height: 1.8;
            font-size: 1.05rem;
            font-weight: 500;
            padding: 5px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Layout principal
    st.markdown('<div class="brand-badge">L\'ORÉAL BRANDSTORM x BARBEXPERT</div>', unsafe_allow_html=True)
    
    # Logo et titre avec jeu de mot
    st.markdown('<div class="logo-text">BARB<span class="logo-accent">EXPERT</span></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">MAÎTRE DE VOTRE BARBE</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Analyse professionnelle & conseils sur mesure</p>', unsafe_allow_html=True)
    
    left_col, right_col = st.columns([1, 2])

    with left_col:
        
        uploaded_file = st.file_uploader(
            "TÉLÉCHARGEZ VOTRE PHOTO",
            type=['png', 'jpg', 'jpeg'],
            help="Limite 200MB par fichier • PNG, JPG, JPEG"
        )

        if uploaded_file:
            st.markdown(f'<img src="data:image/jpeg;base64,{base64.b64encode(uploaded_file.getvalue()).decode()}" class="uploaded-image" style="width:100%">', unsafe_allow_html=True)
            
            if st.button("ANALYSER MA BARBE"):
                with right_col:
                    st.markdown('<h1 class="main-title">VOTRE PROFIL</h1>', 
                              unsafe_allow_html=True)
                    
                    analyzer = BeardAnalyzer()
                    result = analyzer.analyze_image(uploaded_file.getvalue())
                    
                    if result:
                        recommended_style = result["recommended_style"]
                        recommended_color = result["recommended_color"]
                        
                        # Affichage des styles de barbe
                        st.markdown('<h2 class="analysis-title">STYLE RECOMMANDÉ</h2>', 
                                  unsafe_allow_html=True)
                        
                        # Grille des styles améliorée
                        col1, col2 = st.columns(2)
                        cols = [col1, col2]
                        for idx, (name, desc) in enumerate(BEARD_STYLES.items()):
                            with cols[idx % 2]:
                                st.markdown(f"""
                                    <div class="style-box {'selected-style-box' if name == recommended_style else ''}">
                                        <div class="style-name">{name}</div>
                                        <div class="style-desc">{desc}</div>
                                        {f'<div class="selected-badge">RECOMMANDÉ</div>' if name == recommended_style else ''}
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                        
                        # Détails de l'analyse
                        st.markdown('<h2 class="analysis-title">ANALYSE PERSONNALISÉE</h2>', 
                                  unsafe_allow_html=True)
                        
                        # Extraire toutes les données du résultat
                        face_shape = result.get("face_shape", "Non détecté")
                        has_gray = result.get("has_gray", False)
                        trim_length = result.get("trim_length_mm", "5-10")
                        problem_areas = result.get("problem_areas", [])
                        
                        # Extraire les recommandations
                        recommendations = result.get("recommendations", {})
                        trim_advice = recommendations.get("trim", "Non disponible")
                        products = recommendations.get("products", [])
                        routine = recommendations.get("routine", "Non disponible")
                        
                        # Affichage du profil et des recommandations
                        st.markdown('<h2 class="analysis-title">1. CARACTÉRISTIQUES</h2>', unsafe_allow_html=True)
                        
                        st.markdown(f"""
                            <div class="final-choice">
                                <div class="recommendation-item">
                                    <div class="recommendation-label">Style optimal:</div>
                                    <div class="recommendation-value">{recommended_style}</div>
                                </div>
                                <div class="recommendation-item">
                                    <div class="recommendation-label">Forme du visage:</div>
                                    <div class="recommendation-value">{face_shape}</div>
                                </div>
                                <div class="recommendation-item">
                                    <div class="recommendation-label">Présence de gris:</div>
                                    <div class="recommendation-value">{"Oui" if has_gray else "Non"}</div>
                                </div>
                                <div class="recommendation-item">
                                    <div class="recommendation-label">Longueur optimale:</div>
                                    <div class="recommendation-value">{trim_length} mm</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Problèmes spécifiques s'il y en a
                        if problem_areas:
                            st.markdown('<h2 class="analysis-title">POINTS D\'ATTENTION</h2>', unsafe_allow_html=True)
                            
                            problem_html = ""
                            for problem in problem_areas:
                                problem_html += f'<div class="product-item">{problem}</div>'
                            
                            st.markdown(f"""
                                <div class="final-choice">
                                    {problem_html}
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # Affichage des techniques de coupe
                        st.markdown('<h2 class="analysis-title">2. TECHNIQUE DE COUPE</h2>', unsafe_allow_html=True)
                        
                        st.markdown(f"""
                            <div class="final-choice">
                                <div class="recommendation-item">
                                    <div class="recommendation-value">{trim_advice}</div>
                                </div>
                                <div class="recommendation-item">
                                    <div class="recommendation-label">Couleur idéale:</div>
                                    <div class="recommendation-value">{recommended_color}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Affichage des produits L'Oréal recommandés
                        st.markdown('<h2 class="analysis-title">3. PRODUITS RECOMMANDÉS</h2>', unsafe_allow_html=True)
                        
                        if products:
                            products_html = ""
                            for product in products:
                                products_html += f'<div class="product-item">{product}</div>'
                            
                            st.markdown(f"""
                                <div class="final-choice">
                                    {products_html}
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                                <div class="final-choice">
                                    <div class="recommendation-item">
                                        <div class="recommendation-value">Aucun produit spécifique recommandé.</div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # Routine d'entretien
                        st.markdown('<h2 class="analysis-title">4. ROUTINE D\'ENTRETIEN</h2>', unsafe_allow_html=True)
                        
                        st.markdown(f"""
                            <div class="final-choice">
                                <div class="routine-text">{routine}</div>
                            </div>
                        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

