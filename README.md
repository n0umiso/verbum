# Verbum

Verbum is a multilingual Bible reading app.

The current web app is a static HTML experience backed by local JSON Bible data. The `ios` folder contains a native iOS wrapper that bundles the same web app for `WKWebView`.

## Web

Run a local server from the project root:

```sh
python3 -m http.server 8080 --bind 127.0.0.1
```

Then open:

```text
http://127.0.0.1:8080/
```

## iOS

Open:

```text
ios/Verbum.xcodeproj
```

In Xcode, select your signing team and run the `Verbum` target on a simulator or device.

After changing the web app or data, sync the bundled iOS copy:

```sh
sh scripts/sync_ios_web.sh
```
