// src/utils/openPopup.ts
export function openPopup(
  url: string,
  name = 'riot-login',
  width = 500,
  height = 700
): Window | null {
  const left = window.screenX + (window.outerWidth - width) / 2;
  const top  = window.screenY + (window.outerHeight - height) / 2;
  const features = [
    `width=${width}`,
    `height=${height}`,
    `left=${left}`,
    `top=${top}`,
    'resizable,scrollbars'
  ].join(',');

  return window.open(url, name, features);
}
