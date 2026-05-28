import React, { useEffect, useState } from "react";

const API_URL = "https://imgw-etl-project.onrender.com/weather";

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [error, setError] = useState(null);

  const fetchWeatherData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(API_URL);

      if (!response.ok) {
        throw new Error(`Błąd API: ${response.status}`);
      }

      const json = await response.json();

      setData(json);
      setLastRefresh(new Date().toLocaleString("pl-PL"));
    } catch (err) {
      setError("Nie udało się pobrać danych z API.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeatherData();

    const interval = setInterval(fetchWeatherData, 60000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div
      style={{
        padding: "40px",
        fontFamily: "Arial, sans-serif",
        background: "#f1f5f9",
        minHeight: "100vh",
      }}
    >
      <h1>IMGW Weather ETL Dashboard</h1>

      <div
        style={{
          marginTop: "20px",
          marginBottom: "30px",
          padding: "20px",
          background: "white",
          borderRadius: "12px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
        }}
      >
        <h2>Architektura rozwiązania</h2>

        <p>
          Aplikacja realizuje proces ETL pobierający dane pogodowe z API IMGW.
          Dane są filtrowane dla miast rozpoczynających się na litery K i L,
          następnie zapisywane do bazy PostgreSQL w Supabase.
          -<p>--------------------</p>

        </p>

        <p>
          Backend został przygotowany w Python Flask i udostępnia publiczne API,
          natomiast frontend React prezentuje dane w formie dashboardu WWW.
          <p>---------------------</p>
        </p>

        <p>
          ETL uruchamiany jest automatycznie przez Render Cron Job.
          <p>---------------------</p>
        </p>

        <p>
          Backend aplikacji został wdrożony w chmurze Render.com,
          natomiast frontend dashboardu hostowany jest na platformie Vercel.
          <p>---------------------</p>
        </p>

        <strong>
          IMGW API → Python ETL → Supabase PostgreSQL →
          Flask API (Render.com) → React Dashboard (Vercel)
        </strong>
      </div>

      <div style={{ marginBottom: "20px" }}>
        <strong>Liczba rekordów:</strong> {data.length}
        <br />
        <strong>Ostatnie odświeżenie dashboardu:</strong>{" "}
        {lastRefresh || "ładowanie..."}
      </div>

      <button
        onClick={fetchWeatherData}
        style={{
          padding: "10px 16px",
          marginBottom: "20px",
          border: "none",
          borderRadius: "8px",
          background: "#0f172a",
          color: "white",
          cursor: "pointer",
        }}
      >
        Odśwież dane
      </button>

      {loading ? (
        <p>Ładowanie danych...</p>
      ) : error ? (
        <p style={{ color: "red" }}>{error}</p>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table
            border="1"
            cellPadding="10"
            style={{
              width: "100%",
              background: "white",
              borderCollapse: "collapse",
            }}
          >
            <thead style={{ background: "#e2e8f0" }}>
              <tr>
                <th>Miasto</th>
                <th>Temperatura</th>
                <th>Ciśnienie</th>
                <th>Różnica ciśnienia</th>
                <th>Wilgotność</th>
                <th>Wiatr</th>
                <th>Opady</th>
                <th>Data pomiaru</th>
                <th>Godzina pomiaru</th>
                <th>Zapis w bazie</th>
              </tr>
            </thead>

            <tbody>
              {data.map((item, index) => (
                <tr
                  key={`${item.miasto}-${item.data_pomiaru}-${item.godzina_pomiaru}-${index}`}
                >
                  <td>{item.miasto}</td>
                  <td>{item.temperatura} °C</td>
                  <td>{item.cisnienie} hPa</td>
                  <td>{item.roznica_cisnienia} hPa</td>
                  <td>{item.wilgotnosc_wzgledna}%</td>
                  <td>{item.predkosc_wiatru} km/h</td>
                  <td>{item.suma_opadu} mm</td>
                  <td>{item.data_pomiaru}</td>
                  <td>{item.godzina_pomiaru}:00</td>
                  <td>{item.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;