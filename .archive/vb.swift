// My Fist App!
// VB_tracker is my Volleyball Tracker App codded with assistance from Bing CoPilot
// This app tracks Volleyball stats by player and touch
// It allows exporting of match logs in JSON format to support detailed post game analysis
// future versions may add CSV export and graphical analysis
// VB_tracker main app file

import SwiftUI
import UniformTypeIdentifiers

@main
struct VB_tracker: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    var body: some View {
        TabView {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house")
                }

            TeamsView()
                .tabItem {
                    Label("Teams", systemImage: "person.3.fill")
                }

            ScheduleView()
                .tabItem {
                    Label("Schedule", systemImage: "calendar")
                }

            GameView()
                .tabItem {
                    Label("Game", systemImage: "sportscourt")
                }

            ArchiveView()
                .tabItem {
                    Label("Archive", systemImage: "tray.full")
                }
        }
    }
}

struct HomeView: View {
    var body: some View {
        NavigationView {
            Text("🏐 Welcome to VB Tracker")
                .font(.title)
                .padding()
        }
    }
}

// Manage Teams and Players
struct Team: Identifiable, Codable {
    let id = UUID()
    var name: String
    var hometown: String
    var league: String
    var season: String
    var players: [Player] = []
}

struct Player: Identifiable, Codable {
    let id = UUID()
    var name: String
    var jersey: Int
    var position: String
}

class TeamViewModel: ObservableObject {
    @Published var team: Team = Team(name: "", hometown: "", league: "", season: "")
    @Published var newPlayer: Player = Player(name: "", jersey: 0, position: "")

    private let saveURL: URL = {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        return docs.appendingPathComponent("team.json")
    }()

    init() {
        loadTeam()
    }

    func addPlayer() {
        guard !team.players.contains(where: { $0.jersey == newPlayer.jersey }) else { return }
        team.players.append(newPlayer)
        newPlayer = Player(name: "", jersey: 0, position: "")
        saveTeam()
    }

    func saveTeam() {
        do {
            let data = try JSONEncoder().encode(team)
            try data.write(to: saveURL)
        } catch {
            print("❌ Failed to save team: \(error)")
        }
    }

    func loadTeam() {
        do {
            let data = try Data(contentsOf: saveURL)
            team = try JSONDecoder().decode(Team.self, from: data)
        } catch {
            print("⚠️ No saved team found or failed to load: \(error)")
        }
    }
}

struct TeamsView: View {
    @StateObject private var viewModel = TeamViewModel()

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Team Info")) {
                    TextField("Team Name", text: $viewModel.team.name)
                    TextField("Hometown", text: $viewModel.team.hometown)
                    TextField("League", text: $viewModel.team.league)
                    TextField("Season", text: $viewModel.team.season)
                        .onChange(of: viewModel.team.season) { _ in viewModel.saveTeam() }
                }

                Section(header: Text("Add Player")) {
                    TextField("Name", text: $viewModel.newPlayer.name)
                    TextField("Jersey #", value: $viewModel.newPlayer.jersey, format: .number)
                    TextField("Position", text: $viewModel.newPlayer.position)

                    Button("➕ Add Player") {
                        viewModel.addPlayer()
                    }
                    .disabled(
                        viewModel.newPlayer.name.isEmpty ||
                        viewModel.newPlayer.jersey == 0 ||
                        viewModel.team.players.contains(where: { $0.jersey == viewModel.newPlayer.jersey })
                    )
                }

                Section(header: Text("Roster")) {
                    if viewModel.team.players.isEmpty {
                        Text("No players added yet.")
                    } else {
                        ForEach(viewModel.team.players) { player in
                            HStack {
                                Text("#\(player.jersey)")
                                Text(player.name)
                                Spacer()
                                Text(player.position)
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                }
            }
            .navigationTitle("Team Setup")
        }
    }
}

// Schedule Matches
struct Match: Identifiable, Codable {
    let id = UUID()
    var ourTeam: String
    var opponent: String
    var date: Date
    var setFormat: SetFormat
    var pointsToWin: PointsToWin
}

enum SetFormat: String, CaseIterable, Codable {
    case bestOf5 = "Best of 5"
    case bestOf3 = "Best of 3"
    case alwaysPlay3 = "Always Play 3"
}

enum PointsToWin: String, CaseIterable, Codable {
    case twentyFive = "25"
    case twentyFiveFifteen = "25/15"
}

class ScheduleViewModel: ObservableObject {
    @Published var matches: [Match] = []
    @Published var archivedMatches: [Match] = []
    @Published var newMatch = Match(
        ourTeam: "",
        opponent: "",
        date: Date(),
        setFormat: .bestOf5,
        pointsToWin: .twentyFiveFifteen
    )
    
    private let saveURL: URL = {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        return docs.appendingPathComponent("schedule.json")
    }()
    
    private let archiveURL: URL = {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        return docs.appendingPathComponent("archived_matches.json")
    }()

    init() {
        loadMatches()
    }

    func addMatch() {
        matches.append(newMatch)
        newMatch = Match(
            ourTeam: "",
            opponent: "",
            date: Date(),
            setFormat: .bestOf5,
            pointsToWin: .twentyFiveFifteen
        )
        saveMatches()
    }

    func saveMatches() {
        do {
            let data = try JSONEncoder().encode(matches)
            try data.write(to: saveURL)
        } catch {
            print("❌ Failed to save matches: \(error)")
        }
    }

    func loadMatches() {
        do {
            let data = try Data(contentsOf: saveURL)
            matches = try JSONDecoder().decode([Match].self, from: data)
        } catch {
            print("⚠️ No saved matches found or failed to load: \(error)")
        }
    }

    func archiveMatch(_ match: Match) {
        archivedMatches.append(match)
        matches.removeAll { $0.id == match.id }
        saveMatches()
    }

    func saveArchivedMatches() {
        do {
            let data = try JSONEncoder().encode(archivedMatches)
            try data.write(to: archiveURL)
        } catch {
            print("❌ Failed to save archive: \(error)")
        }
    }

    func loadArchivedMatches() {
        do {
            let data = try Data(contentsOf: archiveURL)
            archivedMatches = try JSONDecoder().decode([Match].self, from: data)
        } catch {
            print("⚠️ No archived matches found or failed to load: \(error)")
        }
    }

    func deleteArchivedMatch(_ match: Match) {
        archivedMatches.removeAll { $0.id == match.id }
        saveArchivedMatches()
    }
}

struct ScheduleView: View {
    @StateObject private var scheduleVM = ScheduleViewModel()
    @StateObject private var teamVM = TeamViewModel() // Reuse from TeamsView

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Add Match")) {
                    Picker("Our Team", selection: $scheduleVM.newMatch.ourTeam) {
                        ForEach([teamVM.team.name], id: \.self) { team in
                            Text(team)
                        }
                    }

                    TextField("Opponent Team", text: $scheduleVM.newMatch.opponent)

                    DatePicker("Date", selection: $scheduleVM.newMatch.date, displayedComponents: .date)

                    Picker("Set Format", selection: $scheduleVM.newMatch.setFormat) {
                        ForEach(SetFormat.allCases, id: \.self) { format in
                            Text(format.rawValue)
                        }
                    }

                    Picker("Points to Win", selection: $scheduleVM.newMatch.pointsToWin) {
                        ForEach(PointsToWin.allCases, id: \.self) { points in
                            Text(points.rawValue)
                        }
                    }

                    Button("➕ Add Match") {
                        scheduleVM.addMatch()
                    }
                    .disabled(scheduleVM.newMatch.ourTeam.isEmpty || scheduleVM.newMatch.opponent.isEmpty)
                }

                Section(header: Text("Upcoming Matches")) {
                    if scheduleVM.matches.isEmpty {
                        Text("No matches scheduled.")
                    } else {
                        ForEach(scheduleVM.matches) { match in
                            VStack(alignment: .leading) {
                                Text("\(match.ourTeam) vs \(match.opponent)")
                                    .font(.headline)
                                Text("📅 \(match.date.formatted(date: .abbreviated, time: .omitted))")
                                Text("🎯 \(match.setFormat.rawValue), Points: \(match.pointsToWin.rawValue)")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }
            }
            .navigationTitle("Match Schedule")
        }
    }
}

// Live Game Tracking
func generateMatchFilename(ourTeam: String, theirTeam: String) -> String {
    let formatter = DateFormatter()
    formatter.dateFormat = "yyMMdd"
    let dateString = formatter.string(from: Date())

    let cleanOur = ourTeam.replacingOccurrences(of: " ", with: "_")
    let cleanTheir = theirTeam.replacingOccurrences(of: " ", with: "_")

    return "\(dateString)_\(cleanOur)_\(cleanTheir).json"
}

func saveRallyLog(_ events: [RallyEvent], filename: String) -> URL? {
    let encoder = JSONEncoder()
    encoder.outputFormatting = .prettyPrinted

    do {
        let data = try encoder.encode(events)
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        let fileURL = docs.appendingPathComponent(filename)
        try data.write(to: fileURL)
        return fileURL
    } catch {
        print("❌ Failed to save rally log: \(error)")
        return nil
    }
}

struct RallyEvent: Identifiable, Codable {
    let id = UUID()
    var rotation: Int
    var scoreUs: Int
    var scoreThem: Int
    var rallyStep: Int
    var touchServe: String?
    var touchBlock: String?
    var touchBlockAssist: String?
    var touch1: String?
    var touch2: String?
    var touch3: String?
}

enum RallyPhase {
    case serve
    case rally
    case overNet
    case confirmReturn
}

class GameState: ObservableObject {
    @Published var scoreUs = 0
    @Published var scoreThem = 0
    @Published var rotation = 1
    @Published var rallyStep = 0 // 0 = we serve, 1 = they serve
    @Published var gameOver = false
    @Published var rallyPhase: RallyPhase = .serve
    @Published var rallyEvents: [RallyEvent] = []

    func resetMatch() {
        scoreUs = 0
        scoreThem = 0
        rotation = 1
        rallyStep = 0
        gameOver = false
        rallyEvents = []
        rallyPhase = .serve
    }

    func addRallyEvent(_ event: RallyEvent) {
        rallyEvents.append(event)
    }

    func pointUs() {
        scoreUs += 1
        if rallyStep % 2 == 1 {
            rotation = rotation % 6 + 1
        }
        rallyStep = 0
        checkGameOver()
    }

    func pointThem() {
        scoreThem += 1
        rallyStep = 1
        checkGameOver()
    }

    func checkGameOver() {
        if scoreUs >= 25 && scoreUs >= scoreThem + 2 {
            gameOver = true
        } else if scoreThem >= 25 && scoreThem >= scoreUs + 2 {
            gameOver = true
        }
    }
}

struct ScoreHeaderView: View {
    var ourScore: Int
    var theirScore: Int
    var ourTeam: String
    var theirTeam: String
    var ourSets: Int
    var theirSets: Int

    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Text("\(ourScore)")
                    .font(.system(size: 72, weight: .bold))
                    .frame(maxWidth: .infinity, alignment: .leading)

                Text("\(theirScore)")
                    .font(.system(size: 72, weight: .bold))
                    .frame(maxWidth: .infinity, alignment: .trailing)
            }

            HStack {
                VStack {
                    Text(ourTeam)
                        .font(.title2)
                    Text("Sets: \(ourSets)")
                        .font(.subheadline)
                }
                Spacer()
                VStack {
                    Text(theirTeam)
                        .font(.title2)
                    Text("Sets: \(theirSets)")
                        .font(.subheadline)
                }
            }
        }
        .padding()
    }
}

struct RotationView: View {
    @Binding var rotation: Int
    @Binding var lineup: [Int?] // 6-player rotation
    var players: [Player]

    var body: some View {
        VStack(spacing: 12) {
            Text("Starting Rotation")
                .font(.headline)

            Picker("Initial Rotation", selection: $rotation) {
                ForEach(1...6, id: \.self) { i in
                    Text("Rotation \(i)").tag(i)
                }
            }
            .pickerStyle(SegmentedPickerStyle())

            Grid(horizontalSpacing: 16, verticalSpacing: 8) {
                GridRow {
                    ForEach(0..<3) { i in
                        playerPicker(position: i)
                    }
                }
                GridRow {
                    ForEach(3..<6) { i in
                        playerPicker(position: i)
                    }
                }
            }
        }
        .padding()
    }

    @ViewBuilder
    func playerPicker(position: Int) -> some View {
        Picker("P\(position+1)", selection: $lineup[position]) {
            Text("—").tag(nil as Int?)
            ForEach(players) { player in
                Text("#\(player.jersey) \(player.name)").tag(player.jersey as Int?)
            }
        }
        .labelsHidden()
        .frame(maxWidth: .infinity)
    }
}

struct StartRallyView: View {
    @Binding var firstServe: String?

    var body: some View {
        VStack(spacing: 12) {
            Text("Start Rally")
                .font(.headline)

            Picker("Who serves first?", selection: $firstServe) {
                Text("We Serve").tag("us" as String?)
                Text("We Receive").tag("them" as String?)
            }
            .pickerStyle(SegmentedPickerStyle())

            if firstServe != nil {
                Button("🚀 Start Rally") {
                    // Trigger rally logic here
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding()
    }
}

struct RallyInputView: View {
    @ObservedObject var gameState: GameState
    @State private var serveResult: String?
    @State private var rallyResult: String?
    @State private var touch1: String?
    @State private var touch2: String?
    @State private var touch3: String?

    var body: some View {
        VStack(spacing: 16) {
            if gameState.rallyPhase == .serve {
                Text("Serve Result")
                Picker("Serve", selection: $serveResult) {
                    Text("Ace").tag("Ace" as String?)
                    Text("Error").tag("Error" as String?)
                    Text("Return").tag("Return" as String?)
                }
                .pickerStyle(.segmented)

                Button("Confirm Serve") {
                    handleServe()
                }
                .disabled(serveResult == nil)
            }

            if gameState.rallyPhase == .rally {
                Text("Rally Touches")
                TextField("Touch 1", text: Binding($touch1, replacingNilWith: ""))
                TextField("Touch 2", text: Binding($touch2, replacingNilWith: ""))
                TextField("Touch 3", text: Binding($touch3, replacingNilWith: ""))

                Button("Confirm Rally") {
                    handleRally()
                }
            }

            if gameState.rallyPhase == .confirmReturn {
                Picker("They Rally", selection: $rallyResult) {
                    Text("Error").tag("Error" as String?)
                    Text("Return").tag("Return" as String?)
                }
                .pickerStyle(.segmented)

                Button("Confirm Result") {
                    handleReturn()
                }
                .disabled(rallyResult == nil)
            }
        }
        .padding()
    }

    func handleServe() {
        let event = RallyEvent(
            rotation: gameState.rotation,
            scoreUs: gameState.scoreUs,
            scoreThem: gameState.scoreThem,
            rallyStep: gameState.rallyStep,
            touchServe: "P\(gameState.rotation):\(serveResult ?? "")"
        )
        gameState.addRallyEvent(event)

        switch serveResult {
        case "Ace":
            gameState.pointUs()
        case "Error":
            gameState.pointThem()
        case "Return":
            gameState.rallyPhase = .rally
        default:
            break
        }
    }

    func handleRally() {
        let event = RallyEvent(
            rotation: gameState.rotation,
            scoreUs: gameState.scoreUs,
            scoreThem: gameState.scoreThem,
            rallyStep: gameState.rallyStep,
            touch1: touch1,
            touch2: touch2,
            touch3: touch3
        )
        gameState.addRallyEvent(event)

        if [touch1, touch2, touch3].contains(where: { $0?.contains("Error") == true }) {
            gameState.pointThem()
        } else if [touch1, touch2, touch3].contains(where: { $0?.contains("Kill") == true }) {
            gameState.pointUs()
        } else if [touch1, touch2, touch3].contains(where: { $0?.contains("Over") == true }) {
            gameState.rallyPhase = .confirmReturn
        }
    }

    func handleReturn() {
        if rallyResult == "Error" {
            gameState.pointUs()
        } else {
            gameState.rallyPhase = .rally
        }
    }
}

struct DeadBallView: View {
    @Binding var lineup: [Int?]
    var roster: [Player]
    @ObservedObject var gameState: GameState
    var ourTeam: String
    var theirTeam: String

    @State private var outPlayer: Int?
    @State private var inPlayer: Int?
    @State private var exportURL: URL?

    var body: some View {
        VStack(spacing: 16) {
            Text("Dead Ball Events")
                .font(.headline)

            // Substitution
            Text("Substitute Player")
                .font(.subheadline)

            Picker("Player Out", selection: $outPlayer) {
                Text("—").tag(nil as Int?)
                ForEach(lineup.compactMap { $0 }, id: \.self) { jersey in
                    Text("#\(jersey)").tag(jersey as Int?)
                }
            }

            Picker("Player In", selection: $inPlayer) {
                Text("—").tag(nil as Int?)
                ForEach(roster.map { $0.jersey }, id: \.self) { jersey in
                    Text("#\(jersey)").tag(jersey as Int?)
                }
            }

            Button("🔄 Confirm Substitution") {
                if let out = outPlayer, let `in` = inPlayer,
                   let index = lineup.firstIndex(of: out) {
                    lineup[index] = `in`
                    outPlayer = nil
                    inPlayer = nil
                }
            }
            .disabled(outPlayer == nil || inPlayer == nil)

            Divider()

            // Export
            Text("Match Export")
                .font(.headline)

            Button("💾 Save Rally Log") {
                let filename = generateMatchFilename(ourTeam: ourTeam, theirTeam: theirTeam)
                exportURL = saveRallyLog(gameState.rallyEvents, filename: filename)
            }

            if let url = exportURL {
                ShareLink(item: url, preview: SharePreview("Match Log", image: Image(systemName: "doc.plaintext")))
                    .padding(.top, 8)
            }

            Button("📦 Archive Match") {
                scheduleVM.archiveMatch(scheduleVM.newMatch)
                gameState.resetMatch()
                firstServe = nil
                lineup = Array(repeating: nil, count: 6)
            }

        }
        .padding()
    }
}

struct GameView: View {
    @StateObject private var gameState = GameState()
    @StateObject private var teamVM = TeamViewModel()
    @StateObject private var scheduleVM = ScheduleViewModel()

    @State private var selectedMatch: Match?
    @State private var lineup: [Int?] = Array(repeating: nil, count: 6)
    @State private var rotation = 1
    @State private var firstServe: String? = nil

    var body: some View {
        ScrollView {
            Picker("Select Match", selection: $selectedMatch) {
                ForEach(scheduleVM.matches) { match in
                    Text("\(match.ourTeam) vs \(match.opponent) – \(match.date.formatted(date: .abbreviated, time: .omitted))")
                        .tag(match as Match?)
                }
            }
            .pickerStyle(.menu)
            .padding()

            if let match = selectedMatch {
                ScoreHeaderView(
                    ourScore: gameState.scoreUs,
                    theirScore: gameState.scoreThem,
                    ourTeam: match.ourTeam,
                    theirTeam: match.opponent,
                    ourSets: 0,
                    theirSets: 0
                )

                RotationView(rotation: $rotation, lineup: $lineup, players: teamVM.team.players)
                    .onChange(of: gameState.rotation) { newRotation in
                        rotation = newRotation
                    }

                if gameState.rallyEvents.isEmpty {
                    StartRallyView(firstServe: $firstServe)
                        .onChange(of: firstServe) { selection in
                            gameState.rallyStep = selection == "us" ? 0 : 1
                            gameState.rallyPhase = .serve
                        }
                } else {
                    RallyInputView(gameState: gameState)
                }

                DeadBallView(
                    lineup: $lineup,
                    roster: teamVM.team.players,
                    gameState: gameState,
                    ourTeam: match.ourTeam,
                    theirTeam: match.opponent
                )
            } else {
                Text("Select a match to begin.")
                    .font(.headline)
                    .padding()
            }
        }
        .navigationTitle("Live Match")
    }
}

// Archive of Past Matches
struct ArchiveView: View {
    @StateObject private var scheduleVM = ScheduleViewModel()
    @State private var exportURL: URL?
    @State private var showDeleteConfirm = false
    @State private var matchToDelete: Match?

    var body: some View {
        NavigationView {
            List {
                ForEach(scheduleVM.archivedMatches) { match in
                    VStack(alignment: .leading, spacing: 4) {
                        Text("\(match.ourTeam) vs \(match.opponent)")
                            .font(.headline)
                        Text("📅 \(match.date.formatted(date: .abbreviated, time: .omitted))")
                        Text("🎯 \(match.setFormat.rawValue), Points: \(match.pointsToWin.rawValue)")
                            .font(.subheadline)
                            .foregroundColor(.secondary)

                        HStack {
                            Button("📤 Export Log") {
                                let filename = generateMatchFilename(
                                    ourTeam: match.ourTeam,
                                    theirTeam: match.opponent
                                )
                                exportURL = saveRallyLog(loadRallyLog(for: match), filename: filename)
                            }

                            Button("🗑️ Delete") {
                                matchToDelete = match
                                showDeleteConfirm = true
                            }
                            .foregroundColor(.red)
                        }
                    }
                    .padding(.vertical, 6)
                }
            }
            .navigationTitle("Archived Matches")
            .onAppear {
                scheduleVM.loadArchivedMatches()
            }
            .confirmationDialog("Delete this match?", isPresented: $showDeleteConfirm, titleVisibility: .visible) {
                Button("Delete", role: .destructive) {
                    if let match = matchToDelete {
                        scheduleVM.deleteArchivedMatch(match)
                    }
                }
                Button("Cancel", role: .cancel) {}
            }

            if let url = exportURL {
                ShareLink(item: url, preview: SharePreview("Match Log", image: Image(systemName: "doc.plaintext")))
                    .padding()
            }
        }
    }

    func loadRallyLog(for match: Match) -> [RallyEvent] {
        // Load rally log from file using match ID or filename
        // Placeholder: return empty array or mock data
        return []
    }
}

