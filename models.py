from database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, \
                       String, ForeignKey


class Racket(Base):
    __tablename__ = 'Rackets'
    TerritoryName = Column(String(3), primary_key=True)
    RacketName = Column(String(80), nullable=False)
    Reward = Column(String(100), nullable=True)
    Created = Column(String(200), nullable=True, unique=True)
    Changed = Column(String(60), nullable=True)
    Owner = Column(String(60), nullable=True)
    OwnerName = Column(String(80), nullable=True)
    Sector = Column(String(3), nullable=True)
    Level = Column(String(80), nullable=False)

    def __repr__(self):
        return f'<Racket: {self.TerritoryName}>'

    @property
    def to_dict(self):
        return dict((k, self.__getattribute__(k)) for k in Racket.__dict__.keys() if '_' not in k)

    # Racket.dict_info() provides customized layout
    def dict_info(self):
        return dict(
            TerritoryName=self.TerritoryName,
            RacketName=self.RacketName,
            Reward=self.Reward,
            Created=self.Created,
            Changed=self.Changed,
            Owner=self.Owner,
            OwnerName=self.OwnerName,
            Sector=self.Sector,
            Level=self.Level
        )


class Member(Base):
    __tablename__ = 'Members'
    LastSeen = Column(String(200), nullable=True)
    Status = Column(String(200), nullable=True)
    TornID = Column(String(200), primary_key=True)
    Name = Column(String(200), nullable=True)
    Rank = Column(String(200), nullable=True)
    Level = Column(String(200), nullable=True)
    Age = Column(String(200), nullable=True)
    Refills = Column(String(200), nullable=True)
    Xan = Column(String(200), nullable=True)
    XanThisMonth = Column(String(200), nullable=True)
    LSD = Column(String(200), nullable=True)
    StatEnhancers = Column(String(200), nullable=True)
    Fac = Column(String(200), nullable=True)

    def __repr__(self):
        return f'<Member: {self.Name} [{self.TornID}]>'

    def dict_info(self):
        return dict(
            LastSeen=self.LastSeen,
            Status=self.Status,
            TornID=self.TornID,
            Name=self.Name,
            Rank=self.Rank,
            Age=self.Age,
            Refills=self.Refills,
            Xan=self.Xan,
            XanThisMonth=self.XanThisMonth,
            LSD=self.LSD,
            StatEnhancers=self.StatEnhancersc,
            Fac=self.Fac
        )

class WarBase(Base):
    __tablename__ = 'WarBase'
    LastSeen = Column(String(200), nullable=True)
    Status = Column(String(200), nullable=True)
    TornID = Column(String(200), primary_key=True)
    Name = Column(String(200), nullable=True)
    Rank = Column(String(200), nullable=True)
    Level = Column(String(200), nullable=True)
    Age = Column(String(200), nullable=True)
    Refills = Column(String(200), nullable=True)
    Xan = Column(String(200), nullable=True)
    LSD = Column(String(200), nullable=True)
    StatEnhancers = Column(String(200), nullable=True)

    def __repr__(self):
        return f'<Member: {self.Name} [{self.TornID}]>'

    def dict_info(self):
        return dict(
            LastSeen=self.LastSeen,
            Status=self.Status,
            TornID=self.TornID,
            Name=self.Name,
            Rank=self.Rank,
            Age=self.Age,
            Refills=self.Refills,
            Xan=self.Xan,
            LSD=self.LSD,
            StatEnhancers=self.StatEnhancers
        )

class Settings(Base):
    __tablename__ = 'Settings'
    WarbaseFaction = Column(String(20), primary_key=True)

    def __repr__(self):
        return f'<Settings: {self.WarbaseFaction}>'
    
class Company(Base):
    __tablename__ = 'Companies'
    ID = Column(String(200), primary_key=True)
    CompanyName = Column(String(200), nullable=True)
    Weekly = Column(String(200), nullable=True)
    Daily = Column(String(200), nullable=True)
    Status = Column(String(200), nullable=True)
    Rank = Column(String(200), nullable=True)


class Employees(Base):
    __tablename__ = 'Employee'
    CompanyID = Column(String(200), nullable=True)
    LastSeen = Column(String(200), nullable=True)
    ID = Column(String(200), primary_key=True)
    EmployeeName = Column(String(200), nullable=True)
    Position = Column(String(200), nullable=True)


class OCs(Base):
    __tablename__ = 'OC'
    ID = Column(String(200), primary_key=True)
    Name = Column(String(200), nullable=True)
    CE = Column(String(200), nullable=True)
    PersonalNote = Column(String(200), nullable=True)
    OtherNote = Column(String(200), nullable=True)

    def dict_info(self):
        return dict(
            ID=self.ID,
            Name=self.Name,
            CE=self.CE,
            PersonalNote=self.PersonalNote,
            OtherNote=self.OtherNote,
        )
