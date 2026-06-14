import SwiftUI

@main
struct VerbumApp: App {
    var body: some Scene {
        WindowGroup {
            WebAppView()
                .ignoresSafeArea(.container, edges: .bottom)
        }
    }
}
