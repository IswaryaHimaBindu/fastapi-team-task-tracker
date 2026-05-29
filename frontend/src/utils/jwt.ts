export function getUserIdFromToken(token: string): number | null {
  try {
    const payload = token.split('.')[1];
    if (!payload) return null;
    const decoded = JSON.parse(decodeURIComponent(atob(payload).split('').map((c) => `%${(`00${c.charCodeAt(0).toString(16)}`).slice(-2)}`).join('')));
    return typeof decoded.user_id === 'number' ? decoded.user_id : null;
  } catch {
    return null;
  }
}
