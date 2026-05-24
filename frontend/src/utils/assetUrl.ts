export function getAssetUrl(imageUrl: string): string {
  if (!imageUrl) return '';
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) return imageUrl;
  if (imageUrl.startsWith('/output/')) return imageUrl;
  if (imageUrl.startsWith('/static/')) return imageUrl;
  if (imageUrl.startsWith('/api/output/')) return imageUrl.replace('/api/output/', '/output/');
  return imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`;
}
