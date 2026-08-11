import AppIntents
import Foundation

struct ContactEntity: AppEntity {
    var id: String
    var fullName: String
    var phoneNumber: String

    static var typeDisplayRepresentation: TypeDisplayRepresentation = "Contact"

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: LocalizedStringResource(stringLiteral: fullName),
            subtitle: LocalizedStringResource(stringLiteral: phoneNumber)
        )
    }

    static var defaultQuery = ContactEntityQuery()

    init(from person: ContactPerson) {
        self.id = person.id
        self.fullName = person.fullName
        self.phoneNumber = person.phoneNumber
    }
}

struct ContactEntityQuery: EntityQuery {
    func entities(for identifiers: [String]) async throws -> [ContactEntity] {
        let all = try await ContactsService.shared.fetchAll()
        return all
            .filter { identifiers.contains($0.id) }
            .map { ContactEntity(from: $0) }
    }

    func suggestedEntities() async throws -> [ContactEntity] {
        let all = try await ContactsService.shared.fetchAll()
        return all.map { ContactEntity(from: $0) }
    }
}
