"""
AI Deepfake Truth Verifier - Streamlit Web Application
Main application file
"""

import streamlit as st
from PIL import Image
import time
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from detector import DeepfakeDetector
from database import DeepfakeDatabase

# Page configuration
st.set_page_config(
    page_title="AI Deepfake Truth Verifier",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    .fake-result {
        background-color: #ffebee;
        border: 2px solid #f44336;
    }
    .real-result {
        background-color: #e8f5e9;
        border: 2px solid #4caf50;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_detector():
    """Load the detector model (cached)"""
    return DeepfakeDetector()


@st.cache_resource
def load_database():
    """Load the database connection (cached)"""
    return DeepfakeDatabase()


def main():
    """Main application"""

    # Header
    st.markdown('<h1 class="main-header">🔍 AI Deepfake Truth Verifier</h1>', unsafe_allow_html=True)
    st.markdown("**Detect AI-generated and manipulated images using advanced deep learning**")

    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.info(
            """
            This application uses a pretrained deep learning model to detect:
            - AI-generated faces
            - Deepfake images
            - Face-swapped images
            - Manipulated media
            """
        )

        st.header("📊 Statistics")
        db = load_database()
        stats = db.get_statistics()

        st.metric("Total Predictions", stats.get('total_predictions', 0))

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Real", stats.get('real_count', 0), delta_color="normal")
        with col2:
            st.metric("Fake", stats.get('fake_count', 0), delta_color="inverse")

        if stats.get('average_confidence', 0) > 0:
            st.metric("Avg Confidence", f"{stats.get('average_confidence', 0):.1f}%")

        st.header("🔧 Settings")
        show_confidence = st.checkbox("Show Detailed Probabilities", value=True)
        show_history = st.checkbox("Show Prediction History", value=False)

    # Main content
    tab1, tab2, tab3 = st.tabs(["🔍 Analyze Image", "📜 History", "📖 How It Works"])

    with tab1:
        st.header("Upload Image for Analysis")

        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a face image to check if it's real or AI-generated/manipulated"
        )

        if uploaded_file is not None:
            # Create two columns
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📸 Uploaded Image")
                image = Image.open(uploaded_file)
                st.image(image, use_container_width=True)

            with col2:
                st.subheader("🔬 Analysis Results")

                # Show loading spinner
                with st.spinner("Analyzing image..."):
                    # Save uploaded file temporarily
                    temp_path = Path("uploads") / uploaded_file.name
                    temp_path.parent.mkdir(exist_ok=True)

                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Load detector and make prediction
                    detector = load_detector()

                    start_time = time.time()
                    result = detector.predict(str(temp_path))
                    processing_time = time.time() - start_time

                # Display results
                prediction = result['prediction']
                confidence = result['confidence']

                # Result box with color coding
                result_class = "fake-result" if prediction == "FAKE" else "real-result"
                result_emoji = "⚠️" if prediction == "FAKE" else "✅"

                st.markdown(f"""
                    <div class="result-box {result_class}">
                        <h2>{result_emoji} {prediction}</h2>
                        <h3>Confidence: {confidence:.2f}%</h3>
                    </div>
                """, unsafe_allow_html=True)

                # Detailed probabilities
                if show_confidence:
                    st.subheader("📊 Detailed Analysis")

                    # Progress bars
                    st.write("**Real Probability:**")
                    st.progress(result['real_probability'] / 100)
                    st.write(f"{result['real_probability']:.2f}%")

                    st.write("**Fake Probability:**")
                    st.progress(result['fake_probability'] / 100)
                    st.write(f"{result['fake_probability']:.2f}%")

                # Processing info
                st.info(f"⚡ Processing time: {processing_time:.3f} seconds")

                # Save to database
                db = load_database()
                db.save_prediction(
                    image_name=uploaded_file.name,
                    prediction=prediction,
                    confidence=confidence,
                    real_probability=result['real_probability'],
                    fake_probability=result['fake_probability'],
                    image_path=str(temp_path),
                    model_name="dima806/deepfake_vs_real_image_detection",
                    processing_time=processing_time
                )

                # Interpretation
                st.subheader("💡 Interpretation")
                if prediction == "FAKE":
                    st.warning(
                        f"This image appears to be AI-generated or manipulated with "
                        f"{confidence:.1f}% confidence. The model detected patterns "
                        f"consistent with deepfake or synthetic image generation."
                    )
                else:
                    st.success(
                        f"This image appears to be authentic with {confidence:.1f}% confidence. "
                        f"No significant signs of AI generation or manipulation were detected."
                    )

    with tab2:
        st.header("📜 Prediction History")

        db = load_database()
        recent = db.get_recent_predictions(limit=20)

        if recent:
            st.write(f"Showing last {len(recent)} predictions:")

            for i, pred in enumerate(recent):
                with st.expander(f"{pred['image_name']} - {pred['prediction']} ({pred['confidence']:.1f}%)"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Prediction", pred['prediction'])
                    with col2:
                        st.metric("Confidence", f"{pred['confidence']:.2f}%")
                    with col3:
                        st.metric("Time", pred['timestamp'].split('.')[0] if '.' in str(pred['timestamp']) else pred['timestamp'])

                    if pred['real_probability'] and pred['fake_probability']:
                        st.write(f"**Real:** {pred['real_probability']:.2f}% | **Fake:** {pred['fake_probability']:.2f}%")

        else:
            st.info("No predictions yet. Upload an image to get started!")

    with tab3:
        st.header("📖 How It Works")

        st.markdown("""
        ### 🧠 Technology

        This application uses a **pretrained deep learning model** specifically trained to detect deepfakes and AI-generated images.

        #### Model: `dima806/deepfake_vs_real_image_detection`
        - Based on advanced convolutional neural networks (CNNs)
        - Trained on large datasets of real and fake images
        - Optimized for Apple Silicon (M1/M2/M3 Macs)

        ### 🔍 Detection Process

        1. **Upload**: You upload an image
        2. **Preprocessing**: Image is processed and normalized
        3. **Analysis**: Model analyzes pixel patterns, artifacts, and inconsistencies
        4. **Prediction**: Model outputs probability scores for REAL vs FAKE
        5. **Results**: You see the verdict with confidence score

        ### ⚠️ Limitations

        - Works best with **face images**
        - Accuracy depends on image quality
        - New deepfake techniques may not be detected
        - Should be used as one tool among many for verification

        ### 🎯 Use Cases

        - Social media verification
        - News authentication
        - Research and education
        - Digital forensics

        ### 📊 Performance

        - **Inference Speed**: 50-200ms per image on M1 Mac
        - **Accuracy**: ~85-95% on standard datasets
        - **Supported Formats**: JPG, JPEG, PNG
        """)

        st.info("💡 **Tip**: For best results, use clear, well-lit images of faces.")


if __name__ == "__main__":
    main()
