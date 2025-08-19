const backendUrl = "http://localhost:5000/query"; // Change to your backend URL if deployed

document.getElementById('queryForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const query = document.getElementById('queryInput').value;
    document.getElementById('chromaResults').innerHTML = '<em>Loading...</em>';
    document.getElementById('faissResults').innerHTML = '';
    try {
        const res = await fetch(backendUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        const data = await res.json();
        document.getElementById('chromaResults').innerHTML = `<strong>Chroma:</strong><br>${data.chroma.map(c => `<div>${c}</div>`).join('')}`;
        document.getElementById('faissResults').innerHTML = `<strong>FAISS:</strong><br>${data.faiss.map(f => `<div>${f}</div>`).join('')}`;
    } catch (err) {
        document.getElementById('chromaResults').innerHTML = '<span style="color:red">Error fetching results</span>';
        document.getElementById('faissResults').innerHTML = '';
    }
});
