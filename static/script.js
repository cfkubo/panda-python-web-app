function updateOutput(data) {
    const outputDiv = document.getElementById("output");
    outputDiv.innerHTML = `
        <p>Latitude: ${data.latitude}</p>
        <p>Longitude: ${data.longitude}</p>
    `;
}
