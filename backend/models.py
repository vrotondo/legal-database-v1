from app import db
from datetime import datetime
from enum import Enum

# Enums for status fields
class UserRole(Enum):
    ADMIN = "admin"
    ATTORNEY = "attorney"
    PARALEGAL = "paralegal"
    CLIENT = "client"

class CaseStatus(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    CLOSED = "closed"
    ON_HOLD = "on_hold"

class CaseType(Enum):
    CIVIL = "civil"
    CRIMINAL = "criminal"
    FAMILY = "family"
    CORPORATE = "corporate"
    IMMIGRATION = "immigration"
    PERSONAL_INJURY = "personal_injury"
    REAL_ESTATE = "real_estate"

class DocumentType(Enum):
    CONTRACT = "contract"
    BRIEF = "brief"
    MOTION = "motion"
    CORRESPONDENCE = "correspondence"
    EVIDENCE = "evidence"
    PLEADING = "pleading"
    OTHER = "other"

# Association table for many-to-many relationship between cases and attorneys
case_attorneys = db.Table('case_attorneys',
    db.Column('case_id', db.Integer, db.ForeignKey('cases.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.CLIENT)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_cases = db.relationship('Case', secondary=case_attorneys, back_populates='attorneys')
    time_entries = db.relationship('TimeEntry', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(20))
    zip_code = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    ssn_last_four = db.Column(db.String(4))  # Only store last 4 digits for security
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cases = db.relationship('Case', backref='client', lazy='dynamic')
    documents = db.relationship('Document', backref='client', lazy='dynamic')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Client {self.full_name}>'

class Case(db.Model):
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    case_type = db.Column(db.Enum(CaseType), nullable=False)
    status = db.Column(db.Enum(CaseStatus), nullable=False, default=CaseStatus.ACTIVE)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Important dates
    date_opened = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    date_closed = db.Column(db.Date)
    statute_of_limitations = db.Column(db.Date)
    next_court_date = db.Column(db.DateTime)
    
    # Financial information
    hourly_rate = db.Column(db.Decimal(10, 2), default=0.00)
    estimated_hours = db.Column(db.Integer)
    retainer_amount = db.Column(db.Decimal(10, 2), default=0.00)
    
    # Foreign keys
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    primary_attorney_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attorneys = db.relationship('User', secondary=case_attorneys, back_populates='assigned_cases')
    primary_attorney = db.relationship('User', foreign_keys=[primary_attorney_id])
    documents = db.relationship('Document', backref='case', lazy='dynamic')
    time_entries = db.relationship('TimeEntry', backref='case', lazy='dynamic')
    tasks = db.relationship('Task', backref='case', lazy='dynamic')
    
    def __repr__(self):
        return f'<Case {self.case_number}>'

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # Size in bytes
    mime_type = db.Column(db.String(100))
    document_type = db.Column(db.Enum(DocumentType), default=DocumentType.OTHER)
    
    # Security and versioning
    is_confidential = db.Column(db.Boolean, default=True)
    version = db.Column(db.Integer, default=1)
    checksum = db.Column(db.String(64))  # SHA-256 hash for integrity
    
    # AI-generated metadata
    ai_summary = db.Column(db.Text)
    ai_tags = db.Column(db.String(500))  # Comma-separated tags
    ai_category = db.Column(db.String(100))
    
    # Foreign keys
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    uploaded_by = db.relationship('User', backref='uploaded_documents')
    
    def __repr__(self):
        return f'<Document {self.title}>'

class TimeEntry(db.Model):
    __tablename__ = 'time_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    hours = db.Column(db.Decimal(5, 2), nullable=False)  # Up to 999.99 hours
    rate = db.Column(db.Decimal(10, 2), nullable=False)  # Hourly rate
    date_worked = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    is_billable = db.Column(db.Boolean, default=True)
    is_invoiced = db.Column(db.Boolean, default=False)
    
    # Foreign keys
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def total_amount(self):
        return self.hours * self.rate
    
    def __repr__(self):
        return f'<TimeEntry {self.hours}h @ ${self.rate}/hr>'

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Foreign keys
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_tasks')
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_tasks')
    
    def __repr__(self):
        return f'<Task {self.title}>'