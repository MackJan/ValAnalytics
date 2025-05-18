import type {WebviewTag} from 'electron';
import { parseAuthRedirect } from './parse-auth-redirect';
import type {AuthRedirectData} from "./parseAuthRedirect.ts";

export async function openAuthPopup() : Promise<AuthRedirectData> {
    console.log("pressed")
    return new Promise<ReturnType<typeof parseAuthRedirect>>((resolve, reject) => {
        const valWebView = document.createElement('webview') as WebviewTag;
        valWebView.style.display = 'none';
        valWebView.classList.add('val-webview');
        valWebView.nodeintegration = false;
        valWebView.partition = 'persist:valorant';
        valWebView.allowpopups = true;
        valWebView.webpreferences = 'contextIsolation=no';

        let shownSignIn = false;
        let cleanedUp = false;

        const modal = document.createElement('div');
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        modal.style.display = 'flex';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
        modal.style.zIndex = '1000';

        const closeModal = () => {
            cleanupWebView();
            document.body.removeChild(modal);
            reject('Window closed');
        };

        const cleanupWebView = () => {
            if (cleanedUp) return;
            cleanedUp = true;
            valWebView.removeEventListener('did-redirect-navigation', redirectHandler);
            valWebView.removeEventListener('did-navigate', navigateHandler);
            try {
                valWebView.stop();
            } catch (e) {
                console.error(e);
            }
        };

        const checkForToken = async (event: Electron.DidRedirectNavigationEvent | Electron.DidNavigateEvent) => {
            if (event.url.startsWith('https://playvalorant.com/') && event.url.includes('access_token')) {
                cleanupWebView();
                document.body.removeChild(modal);
                try {
                    resolve(parseAuthRedirect(event.url));
                } catch (e) {
                    reject(e);
                }
            }
        };

        const redirectHandler = (event: Electron.DidRedirectNavigationEvent) => {
            checkForToken(event);
        };

        const navigateHandler = (event: Electron.DidNavigateEvent) => {
            if (event.url.startsWith('https://authenticate.riotgames.com') && !shownSignIn) {
                shownSignIn = true;
                valWebView.style.display = 'block';
                modal.appendChild(valWebView);
                document.body.appendChild(modal);
            }
            checkForToken(event);
        };

        valWebView.addEventListener('did-redirect-navigation', redirectHandler);
        valWebView.addEventListener('did-navigate', navigateHandler);
        valWebView.src = 'https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id=play-valorant-web-prod&response_type=token%20id_token&nonce=1&scope=account%20openid';
        valWebView.style.display = 'block'; // Ensure the webview is visible
        modal.appendChild(valWebView);
        document.body.appendChild(modal); // Append the modal to the DOM immediately

        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.style.position = 'absolute';
        closeButton.style.top = '10px';
        closeButton.style.right = '10px';
        closeButton.addEventListener('click', closeModal);

        modal.appendChild(closeButton);
        document.body.appendChild(valWebView);
    });
}