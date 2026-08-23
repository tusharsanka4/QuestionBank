import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import "./index.css";

const STATES = {
  WELCOME: "welcome",
  UPLOADING: "uploading",
  READY: "ready",
  CHATTING: "chatting",
};

export default function App() {
  const [appState, setAppState] = useState(STATES.WELCOME);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const fileInputRef = useRef(null);
  const inputRef = useRef(null);

  function handleInsertFile() {
    fileInputRef.current.click();
  }

  async function handleFileChange(e) {
    const file = e.target.files[0];
    if (!file) return;

    setAppState(STATES.UPLOADING);

    const formData = new FormData();
    formData.append("file", file);

    try {
      await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
    } catch {
      // still transition even if backend errors
    }

    setTimeout(() => setAppState(STATES.READY), 1800);
    setTimeout(() => setAppState(STATES.CHATTING), 2600);
  }

  async function handleSend() {
    const text = input.trim();
    if (!text || thinking) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setThinking(true);

    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Something went wrong. Is the backend running?" },
      ]);
    } finally {
      setThinking(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  const isWelcome = appState === STATES.WELCOME;
  const isUploading = appState === STATES.UPLOADING;
  const isReady = appState === STATES.READY;
  const isChatting = appState === STATES.CHATTING;

  return (
    <motion.div
      className="app"
      animate={{
        backgroundColor: isWelcome || isUploading ? "#3B6FE0" : "#ffffff",
      }}
      transition={{ duration: 1.2, ease: "easeInOut" }}
    >
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        style={{ display: "none" }}
        onChange={handleFileChange}
      />

      {/* Title */}
      <AnimatePresence>
        {isWelcome && (
          <motion.div
            className="title-block"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16, transition: { duration: 0.5 } }}
            transition={{ duration: 0.8 }}
          >
            <p className="welcome-text">Welcome to</p>
            <motion.h1
              className="main-title"
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
            >
              Question Bank
            </motion.h1>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Orb */}
      <AnimatePresence>
        {(isReady || isChatting) && (
          <motion.div
            className="orb"
            initial={{ scale: 0.3, opacity: 0 }}
            animate={{
              scale: 1,
              opacity: 1,
              x: [0, 14, 0, -14, 0],
              y: [0, -6, 0, -6, 0],
            }}
            transition={{
              scale: { duration: 0.5 },
              opacity: { duration: 0.5 },
              x: { duration: 9, repeat: Infinity, ease: "easeInOut", delay: 0.6 },
              y: { duration: 9, repeat: Infinity, ease: "easeInOut", delay: 0.6 },
            }}
          />
        )}
      </AnimatePresence>

      {/* Thinking pulse */}
      {thinking && (
        <motion.div
          className="orb orb--thinking"
          animate={{ scale: [1, 1.18, 1] }}
          transition={{ duration: 1, repeat: Infinity, ease: "easeInOut" }}
        />
      )}

      {/* Morphing button */}
      <AnimatePresence>
        {(isWelcome || isUploading) && (
          <motion.button
            className="insert-btn"
            onClick={isWelcome ? handleInsertFile : undefined}
            initial={{ opacity: 0, y: 8 }}
            animate={
              isUploading
                ? {
                    width: 56,
                    height: 56,
                    borderRadius: 28,
                    backgroundColor: "#3B6FE0",
                    color: "rgba(255,255,255,0)",
                    border: "2px solid rgba(255,255,255,0.3)",
                    opacity: 1,
                    y: 0,
                  }
                : {
                    width: 160,
                    height: 48,
                    borderRadius: 24,
                    backgroundColor: "#ffffff",
                    color: "#3B6FE0",
                    opacity: 1,
                    y: 0,
                  }
            }
            exit={{ opacity: 0, scale: 0.6, transition: { duration: 0.4 } }}
            transition={{ duration: 0.9, ease: [0.4, 0, 0.2, 1] }}
            whileHover={isWelcome ? { scale: 1.04 } : {}}
            whileTap={isWelcome ? { scale: 0.97 } : {}}
          >
            {isWelcome ? "Insert File" : ""}
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat area */}
      <AnimatePresence>
        {isChatting && (
          <motion.div
            className="chat-area"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <div className="messages">
              {messages.length === 0 && (
                <p className="empty-hint">Ask something about your document.</p>
              )}
              {messages.map((m, i) => (
                <div key={i} className={`message message--${m.role}`}>
                  <p>{m.content}</p>
                </div>
              ))}
              {thinking && (
                <div className="message message--assistant message--thinking">
                  <span className="dot" />
                  <span className="dot" />
                  <span className="dot" />
                </div>
              )}
            </div>

            <div className="input-row">
              <input
                ref={inputRef}
                className="chat-input"
                placeholder="Ask something..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
              />
              <button
                className="send-btn"
                onClick={handleSend}
                disabled={thinking}
              >
                ↑
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}