import SwiftUI
import WebKit

struct WebAppView: UIViewRepresentable {
    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.setURLSchemeHandler(context.coordinator.schemeHandler, forURLScheme: "verbum")
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.isOpaque = false
        webView.backgroundColor = UIColor(red: 0.973, green: 0.969, blue: 0.957, alpha: 1)
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.load(URLRequest(url: URL(string: "verbum://app/index.html")!))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}

    final class Coordinator {
        let schemeHandler = VerbumSchemeHandler()
    }
}

final class VerbumSchemeHandler: NSObject, WKURLSchemeHandler {
    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        guard let url = urlSchemeTask.request.url,
              let fileURL = bundledFileURL(for: url) else {
            urlSchemeTask.didFailWithError(NSError(domain: "Verbum", code: 404))
            return
        }

        do {
            let data = try Data(contentsOf: fileURL)
            let response = URLResponse(
                url: url,
                mimeType: mimeType(for: fileURL),
                expectedContentLength: data.count,
                textEncodingName: "utf-8"
            )
            urlSchemeTask.didReceive(response)
            urlSchemeTask.didReceive(data)
            urlSchemeTask.didFinish()
        } catch {
            urlSchemeTask.didFailWithError(error)
        }
    }

    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {}

    private func bundledFileURL(for url: URL) -> URL? {
        var relativePath = url.path
        if relativePath == "/" || relativePath.isEmpty {
            relativePath = "/index.html"
        }

        guard let decodedPath = relativePath.removingPercentEncoding,
              !decodedPath.contains(".."),
              let resourceURL = Bundle.main.resourceURL else {
            return nil
        }

        let trimmedPath = String(decodedPath.drop(while: { $0 == "/" }))
        let webRoot = resourceURL.appendingPathComponent("Web", isDirectory: true)
        return webRoot.appendingPathComponent(trimmedPath)
    }

    private func mimeType(for fileURL: URL) -> String {
        switch fileURL.pathExtension.lowercased() {
        case "html": return "text/html"
        case "css": return "text/css"
        case "js": return "text/javascript"
        case "json": return "application/json"
        case "png": return "image/png"
        case "jpg", "jpeg": return "image/jpeg"
        case "svg": return "image/svg+xml"
        case "woff": return "font/woff"
        case "woff2": return "font/woff2"
        default: return "application/octet-stream"
        }
    }
}
