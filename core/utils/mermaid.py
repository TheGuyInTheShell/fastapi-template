from typing import List
from sqlalchemy import ForeignKey, inspect
from sqlalchemy.orm import DeclarativeBase


def generate_mermaid_diagram(base_class: type[DeclarativeBase]) -> str:
    """
    Generate a Mermaid ER diagram from SQLAlchemy models.
    
    Args:
        base_class: The SQLAlchemy DeclarativeBase class (e.g., BaseAsync)
    
    Returns:
        A string containing the Mermaid ER diagram syntax
    """
    mermaid_lines = ["erDiagram"]
    
    # Get all tables from metadata
    tables = base_class.metadata.tables
    
    # Track relationships to avoid duplicates
    relationships_added = set()
    
    for table_name, table in tables.items():
        # Skip view tables
        if '_deleted' in table_name or '_exists' in table_name:
            continue
            
        # Start entity definition
        entity_lines = [f"    {table_name} {{"]
        
        # Add table columns
        for column in table.columns:
            # Get column type as string
            col_type = str(column.type)
            
            # Determine column attributes
            attributes = []
            
            # Check if primary key
            if column.primary_key:
                attributes.append("PK")
            
            # Check if foreign key
            if column.foreign_keys:
                attributes.append("FK")
            
            # Check if unique
            if column.unique:
                attributes.append("UK")
            
            # Format: type column_name "constraints"
            attribute_str = ",".join(attributes) if attributes else ""
            
            entity_lines.append(f"        {col_type} {column.name} {attribute_str}".strip())
        
        entity_lines.append("    }")
        
        # Add entity definition to mermaid lines
        mermaid_lines.extend(entity_lines)
    
    # Add relationships
    for table_name, table in tables.items():
        # Skip view tables
        if '_deleted' in table_name or '_exists' in table_name:
            continue
            
        for column in table.columns:
            if column.foreign_keys:
                for fk in column.foreign_keys:
                    # Extract referenced table name
                    referenced_table = fk.column.table.name
                    
                    # Create a unique identifier for this relationship
                    rel_id = f"{table_name}-{referenced_table}-{column.name}"
                    
                    # Only add if not already added
                    if rel_id not in relationships_added:
                        # Format: parent ||--o{ child : "foreign_key_name"
                        # Using zero-or-more (o{) for the child side as it's more common
                        mermaid_lines.append(f'    {referenced_table} ||--o{{ {table_name} : "{column.name}"')
                        relationships_added.add(rel_id)
    
    return "\n".join(mermaid_lines)

