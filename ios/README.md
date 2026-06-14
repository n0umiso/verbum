# Verbum iOS

This folder contains a small native iOS wrapper for the Verbum web app.

Open `Verbum.xcodeproj` in Xcode, select the `Verbum` target, choose your signing team, then run on an iPhone simulator or device.

The app bundles `Resources/Web/index.html` and `Resources/Web/data`, then serves them to `WKWebView` through the custom `verbum://` URL scheme. This keeps the existing `fetch("data/...")` calls working without a remote server.

When the root web app changes, sync the bundled copy:

```sh
sh scripts/sync_ios_web.sh
```
