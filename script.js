
async function loadMangaWiserCatalog() {
    const sections = {
        manga: document.querySelector("#latest-manga .release-slider"),
        manhwa: document.querySelector("#latest-manhwa .release-slider"),
        manhua: document.querySelector("#latest-manhua .release-slider"),
        novel: document.querySelector("#latest-novel .release-slider"),
        oneshot: document.querySelector("#latest-oneshot .release-slider")
    };

    function getTitle(item) {
        return item.title?.english ||
            item.title?.romaji ||
            item.title?.native ||
            "Untitled";
    }

    function createCard(item, category) {
        const card = document.createElement("article");
        card.className = "release-card";

        const imageBox = document.createElement("div");
        imageBox.className = "release-image";

        const imageUrl =
            item.coverImage?.extraLarge ||
            item.coverImage?.large;

        if (imageUrl) {
            const image = document.createElement("img");
            image.src = imageUrl;
            image.alt = getTitle(item);
            image.loading = "lazy";
            image.style.width = "100%";
            image.style.height = "100%";
            image.style.objectFit = "cover";

            imageBox.appendChild(image);
        }

        const info = document.createElement("div");
        info.className = "release-info";

        const type = document.createElement("span");
        type.className = "release-type";

        const categoryNames = {
            manga: "Manga",
            manhwa: "Manhwa",
            manhua: "Manhua",
            novel: "Novel / Web Novel",
            oneshot: "One-shot"
        };

        type.textContent = categoryNames[category] || category;

        const title = document.createElement("h3");
        title.textContent = getTitle(item);

        const details = document.createElement("p");

        if (item.chapters) {
            details.textContent = `${item.chapters} chapters`;
        } else if (item.volumes) {
            details.textContent = `${item.volumes} volumes`;
        } else {
            details.textContent = item.status
                ? item.status.replaceAll("_", " ")
                : "Catalog information";
        }

        const link = document.createElement("a");
        link.href = item.siteUrl || "#";
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "View Details";
        link.style.display = "inline-block";
        link.style.marginTop = "8px";

        info.append(type, title, details, link);
        card.append(imageBox, info);

        return card;
    }

    try {
        const response = await fetch("data/anilist-catalog.json");

        if (!response.ok) {
            throw new Error("Catalog JSON could not be loaded.");
        }

        const catalog = await response.json();

        for (const category of Object.keys(sections)) {
            const slider = sections[category];
            const items = catalog.categories?.[category] || [];

            if (!slider || items.length === 0) {
                console.warn(`No catalog entries found for ${category}.`);
                continue;
            }

            slider.replaceChildren();

            items.forEach(item => {
                slider.appendChild(createCard(item, category));
            });
        }

        console.log("Manga Wiser catalog loaded successfully.");

    } catch (error) {
        console.error("Manga Wiser catalog error:", error);
    }
}

document.addEventListener("DOMContentLoaded", loadMangaWiserCatalog);
