export default function Home() {
  return (
    <main style={{ padding: '2rem', textAlign: 'center' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>LINEログインテスト</h1>
      <a href="http://localhost:8000/api/auth/line/login">
        <button
          style={{
            padding: '0.75rem 1.5rem',
            fontSize: '1rem',
            backgroundColor: '#06C755',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: 'pointer',
          }}
        >
          LINEでログイン
        </button>
      </a>
    </main>
  );
}
