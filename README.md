# AI Reflective Voice Coach (Thai) 🇹🇭

An AI-powered voice coach that guides Thai learners through **Gibbs' Reflective Cycle** (6 stages) after a learning event. Built with high-speed multimodal AI for natural human-like conversation and low latency.

## Core Features
- **Gibbs' Reflective Cycle**: Guided 6-stage reflection (Description, Feelings, Evaluation, Analysis, Conclusion, Action Plan).
- **Thai Nuance Support**: Tuned Voice Activity Detection (VAD) to handle Thai fillers like 'เอ่อ', 'อืม'.
- **Low Latency**: Uses Gemini 3.1 Flash Live Preview via LiveKit for <400ms latency.
- **Automated Synthesis**: Generates a structured 6-part Markdown report in Thai after each session.

## Tech Stack
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React (Vite, Tailwind CSS, TypeScript)
- **Real-time Voice**: LiveKit Agents & Server (WebRTC)
- **AI Models**:
    - `gemini-3.1-flash-live-preview` (Real-time interaction)
    - `gemini-1.5-flash` (Post-session synthesis)
- **Database**: PostgreSQL (SQLAlchemy)
- **Orchestration**: Docker Compose

## Prerequisites
- Docker and Docker Compose
- Google AI (Gemini) API Key

## Getting Started

1. **Clone the repository**
2. **Setup Environment Variables**:
   ```bash
   cp example.env .env
   ```
   Edit `.env` and add your `GOOGLE_API_KEY`.

3. **Launch with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

4. **Access the Application**:
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - LiveKit Server: `http://localhost:7880`

## Project Structure
- `backend/`: FastAPI application and AI Agent worker logic.
- `frontend/`: React application and LiveKit UI components.
- `docker-compose.yml`: Orchestrates DB, LiveKit Server, Backend, Agent, and Frontend.

## Usage
1. Enter the **Context** of your learning event on the home screen.
2. Click **"เริ่มการสนทนา"** (Start Conversation).
3. Talk to the coach! The coach will guide you through the 6 stages.
4. Click **"จบการสนทนา"** (End Session) when finished.
5. Wait a few seconds for the AI to synthesize your **Gibbs' Report**.
6. Review your reflection and start a new session if needed.

## Thai VAD Tuning
The system is optimized for Thai language conversation:
- `silence_threshold`: 0.15
- `silence_timeout`: 1.0s
- `min_speech_duration`: 0.3s
