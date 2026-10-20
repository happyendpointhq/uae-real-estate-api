// UAE Real Estate API quickstart (Bayut and PropertyFinder). Node 18+, no dependencies.
//   RAPIDAPI_KEY=... node quickstart.mjs "Dubai Marina"

const HOST = 'uae-real-estate-api.p.rapidapi.com';

async function get(path, platform, params = {}) {
  const url = new URL(`https://${HOST}${path}`);
  url.searchParams.set('platform', platform);
  for (const [key, value] of Object.entries(params)) {
    if (value != null) url.searchParams.set(key, value);
  }
  const res = await fetch(url, {
    headers: { 'x-rapidapi-host': HOST, 'x-rapidapi-key': process.env.RAPIDAPI_KEY },
  });
  const body = await res.json();
  if (!body.success) throw new Error(`${body.error ?? res.status}: ${body.message ?? ''}`);
  return body.data;
}

const area = process.argv[2] ?? 'Dubai Marina';

// Location IDs differ between platforms, so resolve the name on each one.
for (const platform of ['bayut', 'propertyfinder']) {
  const [place] = await get('/autocomplete', platform, { query: area });
  console.log(`${platform}: ${place?.name} id=${place?.location_id}${place?.path ? ` (${place.path})` : ''}`);
}

const [bayutPlace] = await get('/autocomplete', 'bayut', { query: area });
const results = await get('/search-properties', 'bayut', {
  purpose: 'rent',
  location_id: bayutPlace.location_id,
  bedrooms: '1,2',
  sort: 'price_low',
});
console.log(`${results.total} Bayut rentals`);
for (const row of results.properties) {
  console.log(`AED ${row.price.toLocaleString()} / ${row.rentFrequency}  ${row.title?.en ?? row.title}`);
}
