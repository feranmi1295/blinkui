# State Management

BlinkUI uses reactive state. When a `state()` variable changes the screen re-renders automatically.

## Declaring state
```python
from blinkui import Screen, state

class CounterScreen(Screen):
    count    = state(0)
    name     = state("John")
    loading  = state(False)
    items    = state([])
```

## Using state in build
```python
def build(self):
    return VStack(
        Text(f"Hello {self.name}"),
        Text(f"Count: {self.count}"),
    )
```

## Updating state

Assign a new value anywhere in your screen:
```python
def increment(self):
    self.count += 1

def set_name(self, name):
    self.name = name

def load_data(self):
    self.loading = True
    # fetch data...
    self.items = ["item1", "item2"]
    self.loading = False
```

Every assignment triggers a re-render automatically.

## Conditional rendering
```python
def build(self):
    return VStack(
        Spinner() if self.loading else Text("Ready"),
        Button("Load").on_tap(self.load),
    )
```

## State with async
```python
async def on_mount(self):
    self.loading = True
    response = await get("https://api.example.com/data")
    self.items = response.data
    self.loading = False
```