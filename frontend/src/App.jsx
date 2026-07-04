import { useState } from "react";

function App() {
    const [phase, setPhase] = useState("welcome");

    return (
        <main className="landing">
            <h1 className="title">
                Welcome to
                <br />
                <span className="product-name">
                    Question Bank
                </span>
            </h1>

            {phase === "welcome" && (
                <button
                    className="upload-button"
                    onClick={() => setPhase("uploading")}
                >
                    Insert File
                </button>
            )}

            {phase === "uploading" && (
                <div className="orb"></div>
            )}
        </main>
    );
}

export default App;
