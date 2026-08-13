async function loadWeather() {
    const container = document.getElementById("weather-container");

    container.innerHTML = "<p>Getting your location...</p>";

    if (!navigator.geolocation) {
        container.innerHTML = "<p>Geolocation is not supported by your browser.</p>";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        async function(position) {

            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            console.log("Location:", latitude, longitude);

            try {

                const response = await fetch(
                    `/weather?latitude=${latitude}&longitude=${longitude}`
                );

                if (!response.ok) {
                    throw new Error(`Weather request failed: ${response.status}`);
                }

                const weather = await response.json();

                console.log("Weather:", weather);

                const current = weather.current;
                const daily = weather.daily;

                container.innerHTML = `
                    <div class="weather-card">

                        <h2>Local Weather</h2>

                        <div class="weather-temperature">
                            ${Math.round(current.temperature_2m)}°F
                        </div>

                        <p>
                            Feels like
                            ${Math.round(current.apparent_temperature)}°F
                        </p>

                        <p>
                            Humidity:
                            ${current.relative_humidity_2m}%
                        </p>

                        <p>
                            Wind:
                            ${Math.round(current.wind_speed_10m)} mph
                        </p>

                        <p>
                            High:
                            ${Math.round(daily.temperature_2m_max[0])}°F
                        </p>

                        <p>
                            Low:
                            ${Math.round(daily.temperature_2m_min[0])}°F
                        </p>

                    </div>
                `;

            } catch (error) {

                console.error("Weather API error:", error);

                container.innerHTML =
                    "<p>Unable to load weather.</p>";
            }
        },

        function(error) {

            console.error("Location error:", error);

            container.innerHTML = `
                <div class="weather-card">
                    <h2>Location Required</h2>
                    <p>Unable to access your location.</p>
                    <p>${error.message}</p>
                </div>
            `;
        }
    );
}


async function loadNews(category = "") {

    const container = document.getElementById("news-container");

    container.innerHTML = "<p>Loading news...</p>";

    let url = "/news";

    if (category) {
        url += `?category=${category}`;
    }

    try {

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error("News request failed");
        }

        const articles = await response.json();

        container.innerHTML = "";

        articles.forEach(article => {

            const card = document.createElement("article");

            card.className = "news-card";

            card.innerHTML = `
                ${
                    article.image
                    ? `<img src="${article.image}" class="news-image" alt="">`
                    : ""
                }

                <div class="source">
                    ${article.source}
                </div>

                <h2>
                    <a href="${article.link}" target="_blank">
                        ${article.title}
                    </a>
                </h2>

                <p>
                    ${article.summary || ""}
                </p>

                <small>
                    ${article.published || ""}
                </small>
            `;

            container.appendChild(card);
        });

    } catch (error) {

        console.error("News error:", error);

        container.innerHTML =
            "<p>Unable to load news.</p>";
    }
}


loadWeather();
loadNews();