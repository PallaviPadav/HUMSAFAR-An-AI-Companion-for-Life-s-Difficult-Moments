import sys


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


from flask import Flask, render_template, request, jsonify

from services.conversation_service import ConversationService
from utils.logger import get_logger


# =========================================================
# LOGGER
# =========================================================

logger = get_logger(__name__)


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static",
    static_url_path="/static",
)


# =========================================================
# CONVERSATION SERVICE
# =========================================================

conversation_service = ConversationService()


# =========================================================
# HOME PAGE
# =========================================================


@app.route("/", methods=["GET"])
def home():
    logger.info("Inside home")

    return render_template("home.html")


# =========================================================
# CHAT PAGE - GET
# =========================================================


@app.route("/chat", methods=["GET"])
def chat_page():
    logger.info("Inside chat page")

    return render_template("chat.html", message=[])


# =========================================================
# CHAT MESSAGE - POST
# =========================================================


@app.route("/chat", methods=["POST"])
def chat_message():
    logger.info("Inside chat message")
    inspirational_videos = []

    # =====================================================
    # GET TEXT MESSAGE
    # =====================================================

    user_message = request.form.get("message", "").strip()

    logger.info("User message: %s", user_message)

    # =====================================================
    # GET CONVERSATION ID
    # =====================================================

    conversation_id = request.form.get("conversation_id")

    logger.info("Conversation ID: %s", conversation_id)

    # =====================================================
    # GET UPLOADED IMAGE
    # =====================================================

    image_file = request.files.get("image")

    logger.info("Image uploaded: %s", image_file is not None)

    # =====================================================
    # VALIDATE MESSAGE / IMAGE
    # =====================================================

    # User must provide either:
    #     1. a text message
    #     OR
    #     2. an image

    if not user_message and not image_file:
        logger.warning("No message or image received")

        return jsonify({"error": "Please enter a message or upload an image."}), 400

    # =====================================================
    # VALIDATE CONVERSATION ID
    # =====================================================

    if not conversation_id:
        logger.warning("Conversation ID missing")

        return jsonify({"error": "conversation_id is required."}), 400

    # =====================================================
    # PROCESS REQUEST
    # =====================================================

    try:
        # =================================================
        # CASE 1: IMAGE UPLOAD
        # =================================================

        if image_file:
            logger.info("Processing uploaded image")

            # -------------------------------------------------
            # Import vision service only when an image
            # is actually uploaded.
            # -------------------------------------------------

            from services.vision_service import image_to_text_response

            # -------------------------------------------------
            # Send image + user's message to vision service
            # -------------------------------------------------

            response = image_to_text_response(image_file, user_message)

            logger.info("Response from Vision Service: %s", response)

        # =================================================
        # CASE 2: NORMAL TEXT MESSAGE
        # =================================================

        else:
            logger.info("Processing normal text message")

            conversation_result = conversation_service.respond(
                user_message=user_message, conversation_id=conversation_id
            )

            response = conversation_result.get("response", "")

            inspirational_videos = conversation_result.get("inspirational_videos", [])

            logger.info("Response from ConversationService: %s", response)

            logger.info("Inspirational videos returned: %d", len(inspirational_videos))
        # =================================================
        # RETURN RESPONSE TO JAVASCRIPT
        # =================================================

        return jsonify(
            {
                "response": response,
                "conversation_id": conversation_id,
                "inspirational_videos": inspirational_videos,
            }
        )

    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as e:
        logger.exception("Error while processing chat message")

        return jsonify(
            {"error": "Something went wrong while processing your message."}
        ), 500


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
