import Foundation
import Contacts

struct ContactPerson: Identifiable, Hashable, Codable, Sendable {
    let id: String
    let fullName: String
    let phoneNumber: String
}

extension ContactPerson {
    init?(from contact: CNContact) {
        guard let phone = contact.phoneNumbers.first?.value.stringValue else { return nil }
        self.id = contact.identifier
        self.fullName = CNContactFormatter.string(from: contact, style: .fullName) ?? contact.givenName
        self.phoneNumber = phone
    }
}
