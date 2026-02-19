import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Item } from '../item';
import { ItemService } from '../item.service';

@Component({
  selector: 'app-item-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './item-form.component.html',
  styleUrls: ['./item-form.component.css']
})
export class ItemFormComponent implements OnInit {
  item: Item = { name: '', description: '' };
  isEditMode = false;
  itemId?: number;

  constructor(
    private itemService: ItemService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.itemId = this.route.snapshot.params['id'];
    if (this.itemId) {
      this.isEditMode = true;
      this.itemService.getItem(this.itemId).subscribe({
        next: item => this.item = item,
        error: err => console.error('Failed to load item', err)
      });
    }
  }

  save(): void {
    if (this.isEditMode && this.itemId) {
      this.itemService.updateItem(this.itemId, this.item).subscribe({
        next: () => this.router.navigate(['/items']),
        error: err => console.error('Failed to update item', err)
      });
    } else {
      this.itemService.createItem(this.item).subscribe({
        next: () => this.router.navigate(['/items']),
        error: err => console.error('Failed to create item', err)
      });
    }
  }

  cancel(): void {
    this.router.navigate(['/items']);
  }
}
