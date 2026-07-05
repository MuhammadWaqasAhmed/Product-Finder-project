import { useEffect, useMemo, useState } from "react";
import { fetchDashboard, searchProducts } from "./api";
import "./App.css";

const DEFAULT_FILTERS = {
  q: "",
  category: "",
  brand: "",
  min_price: "",
  max_price: "",
  in_stock_only: false,
  limit: 10,
};

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function StatsGrid({ dashboard, searchMeta }) {
  const cards = [
    { label: "Catalog Size", value: dashboard?.total_products ?? "—" },
    { label: "Matches Found", value: searchMeta?.total_matches ?? 0 },
    { label: "Avg Rating", value: searchMeta?.avg_rating ?? dashboard?.top_rated?.[0]?.rating ?? "—" },
    {
      label: "Price Range",
      value: dashboard
        ? `${formatCurrency(dashboard.price_summary.min)} – ${formatCurrency(dashboard.price_summary.max)}`
        : "—",
    },
  ];

  return (
    <section className="stats-grid">
      {cards.map((card) => (
        <article className="stat-card" key={card.label}>
          <p className="stat-card__label">{card.label}</p>
          <p className="stat-card__value">{card.value}</p>
        </article>
      ))}
    </section>
  );
}

function FiltersPanel({ filters, categories, brands, onChange, onApply, onReset }) {
  return (
    <section className="panel filters">
      <h2 className="panel__title">Filters</h2>

      <label>
        Category
        <select
          value={filters.category}
          onChange={(event) => onChange("category", event.target.value)}
        >
          <option value="">All categories</option>
          {categories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </label>

      <label>
        Brand
        <select value={filters.brand} onChange={(event) => onChange("brand", event.target.value)}>
          <option value="">All brands</option>
          {brands.map((brand) => (
            <option key={brand} value={brand}>
              {brand}
            </option>
          ))}
        </select>
      </label>

      <label>
        Min price
        <input
          type="number"
          min="0"
          value={filters.min_price}
          onChange={(event) => onChange("min_price", event.target.value)}
          placeholder="0"
        />
      </label>

      <label>
        Max price
        <input
          type="number"
          min="0"
          value={filters.max_price}
          onChange={(event) => onChange("max_price", event.target.value)}
          placeholder="No max"
        />
      </label>

      <label className="filters__checkbox">
        <input
          type="checkbox"
          checked={filters.in_stock_only}
          onChange={(event) => onChange("in_stock_only", event.target.checked)}
        />
        In stock only
      </label>

      <div className="filters__actions">
        <button type="button" onClick={onApply}>
          Apply filters
        </button>
        <button type="button" onClick={onReset}>
          Reset
        </button>
      </div>
    </section>
  );
}

function ProductCard({ product, rank }) {
  return (
    <article className="product-card">
      <div className="product-card__top">
        <div>
          <p className="product-card__meta">
            #{rank} · {product.brand} · {product.category}
          </p>
          <h3>{product.name}</h3>
        </div>
        <div className="product-card__score">{Math.round(product.score)}</div>
      </div>

      <p className="product-card__price">{formatCurrency(product.price)}</p>
      <p className="product-card__rating">
        {product.rating.toFixed(1)} ★ · {product.reviews.toLocaleString()} reviews
      </p>
      <p className="product-card__description">{product.description}</p>

      <div className="product-card__tags">
        {product.tags.slice(0, 4).map((tag) => (
          <span key={tag}>{tag}</span>
        ))}
      </div>

      <span className={`stock-badge ${product.in_stock ? "stock-badge--in" : "stock-badge--out"}`}>
        {product.in_stock ? "In stock" : "Out of stock"}
      </span>

      {product.match_reasons?.length > 0 && (
        <ul className="product-card__reasons">
          {product.match_reasons.map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ul>
      )}
    </article>
  );
}

export default function App() {
  const [dashboard, setDashboard] = useState(null);
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [draftQuery, setDraftQuery] = useState("");
  const [searchMeta, setSearchMeta] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const categories = useMemo(
    () => searchMeta?.categories ?? dashboard?.categories?.map((item) => item.name) ?? [],
    [dashboard, searchMeta],
  );

  const brands = searchMeta?.brands ?? [];

  async function runSearch(nextFilters = filters) {
    setLoading(true);
    setError("");

    try {
      const payload = await searchProducts({
        q: nextFilters.q,
        category: nextFilters.category,
        brand: nextFilters.brand,
        min_price: nextFilters.min_price,
        max_price: nextFilters.max_price,
        in_stock_only: nextFilters.in_stock_only,
        limit: nextFilters.limit,
      });

      setSearchMeta(payload);
      setResults(payload.results);
    } catch (requestError) {
      setError(requestError.message || "Unable to load search results.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        const dashboardData = await fetchDashboard();
        setDashboard(dashboardData);
        await runSearch(DEFAULT_FILTERS);
      } catch (requestError) {
        setError(requestError.message || "Unable to load dashboard.");
        setLoading(false);
      }
    }

    bootstrap();
  }, []);

  function updateFilter(key, value) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  function handleSearchSubmit(event) {
    event.preventDefault();
    const nextFilters = { ...filters, q: draftQuery.trim() };
    setFilters(nextFilters);
    runSearch(nextFilters);
  }

  function handleApplyFilters() {
    runSearch(filters);
  }

  function handleResetFilters() {
    setDraftQuery("");
    setFilters(DEFAULT_FILTERS);
    runSearch(DEFAULT_FILTERS);
  }

  return (
    <main className="dashboard">
      <header className="dashboard__header">
        <div>
          <p className="dashboard__eyebrow">Product Finder</p>
          <h1 className="dashboard__title">Search & Discovery Dashboard</h1>
          <p className="dashboard__subtitle">
            Search the catalog, rank the best matches, and explore inventory insights in one place.
          </p>
        </div>
        <span className="dashboard__status">API connected</span>
      </header>

      <StatsGrid dashboard={dashboard} searchMeta={searchMeta} />

      <form className="search-bar panel" onSubmit={handleSearchSubmit}>
        <input
          type="search"
          value={draftQuery}
          onChange={(event) => setDraftQuery(event.target.value)}
          placeholder="Search products, brands, categories, or tags..."
          aria-label="Search products"
        />
        <button type="submit">Search</button>
      </form>

      <div className="layout-grid">
        <aside className="sidebar-stack">
          <FiltersPanel
            filters={filters}
            categories={categories}
            brands={brands}
            onChange={updateFilter}
            onApply={handleApplyFilters}
            onReset={handleResetFilters}
          />

          <section className="panel">
            <h2 className="panel__title">Categories</h2>
            <ul className="category-list">
              {(dashboard?.categories ?? []).map((item) => (
                <li key={item.name}>
                  <span>{item.name}</span>
                  <strong>{item.count}</strong>
                </li>
              ))}
            </ul>
          </section>

          <section className="panel">
            <h2 className="panel__title">Top Rated</h2>
            <ul className="top-rated-list">
              {(dashboard?.top_rated ?? []).map((product) => (
                <li key={product.id}>
                  <span>{product.name}</span>
                  <strong>{product.rating.toFixed(1)} ★</strong>
                </li>
              ))}
            </ul>
          </section>
        </aside>

        <section className="panel">
          <div className="results-header">
            <div>
              <h2>Top matching products</h2>
              <p>
                {searchMeta?.query
                  ? `Showing ranked results for "${searchMeta.query}"`
                  : "Showing top catalog picks"}
              </p>
            </div>
            <p>{searchMeta?.total_matches ?? 0} results</p>
          </div>

          {loading && <div className="loading-state">Loading results...</div>}
          {!loading && error && <div className="error-state">{error}</div>}
          {!loading && !error && results.length === 0 && (
            <div className="empty-state">No products matched your search. Try different keywords or filters.</div>
          )}

          {!loading && !error && results.length > 0 && (
            <div className="product-grid">
              {results.map((product, index) => (
                <ProductCard key={product.id} product={product} rank={index + 1} />
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
