const currency = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

function renderProduct(product, rank) {
  return `
    <article class="product-card">
      <img src="${product.image_url}" alt="${product.name}" />
      <div class="product-card__body">
        <p class="product-card__meta">#${rank} · ${product.provider} · ${product.brand}</p>
        <h3>${product.name}</h3>
        <div><span class="score-pill">${Math.round(product.score)}</span></div>
        <strong>${currency.format(product.price)}</strong>
        <p class="product-card__meta">${product.rating.toFixed(1)} ★ · ${product.reviews.toLocaleString()} reviews</p>
        <p class="product-card__meta">${product.description}</p>
        <a href="${product.product_url}" target="_blank" rel="noopener">View listing</a>
      </div>
    </article>
  `;
}

function fillSelect(id, values) {
  const select = document.getElementById(id);
  const current = select.value;
  select.innerHTML = `<option value="">All</option>`;
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
  select.value = current;
}

async function runSearch(query = "") {
  const params = new URLSearchParams();
  if (query) params.set("q", query);
  const category = document.getElementById("filter-category").value;
  const brand = document.getElementById("filter-brand").value;
  const minPrice = document.getElementById("filter-min-price").value;
  const maxPrice = document.getElementById("filter-max-price").value;
  const inStock = document.getElementById("filter-in-stock").checked;
  if (category) params.set("category", category);
  if (brand) params.set("brand", brand);
  if (minPrice) params.set("min_price", minPrice);
  if (maxPrice) params.set("max_price", maxPrice);
  if (inStock) params.set("in_stock_only", "true");

  const response = await fetch(`/api/search?${params.toString()}`);
  const data = await response.json();
  fillSelect("filter-category", data.categories);
  fillSelect("filter-brand", data.brands);

  const meta = document.getElementById("search-meta");
  meta.textContent = data.query
    ? `${data.total_matches} matches for "${data.query}" · Live: ${data.live_providers.join(", ") || "none"} · Demo: ${data.demo_providers.join(", ")}`
    : `${data.total_matches} top catalog picks across ${data.providers.length} sources`;

  document.getElementById("product-grid").innerHTML = data.results
    .map((product, index) => renderProduct(product, index + 1))
    .join("");
}

document.addEventListener("DOMContentLoaded", () => {
  runSearch();
  document.getElementById("search-form").addEventListener("submit", (event) => {
    event.preventDefault();
    runSearch(document.getElementById("search-input").value.trim());
  });
});
