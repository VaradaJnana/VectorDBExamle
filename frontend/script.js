// Use relative path for API endpoint to support deployment on Render or similar platforms
const backendUrl = "/query";

document.getElementById('queryForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const query = document.getElementById('queryInput').value;
    document.getElementById('loader').style.display = 'block';
    document.getElementById('chromaResults').innerHTML = '';
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
    } finally {
        document.getElementById('loader').style.display = 'none';
    }
});
