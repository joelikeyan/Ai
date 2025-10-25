#include "CoffeeMachine.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SphereComponent.h"
#include "Components/WidgetComponent.h"
#include "Engine/Engine.h"

ACoffeeMachine::ACoffeeMachine()
{
    PrimaryActorTick.bCanEverTick = true;

    // Create machine mesh
    MachineMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MachineMesh"));
    RootComponent = MachineMesh;

    // Create interaction sphere
    InteractionSphere = CreateDefaultSubobject<USphereComponent>(TEXT("InteractionSphere"));
    InteractionSphere->SetupAttachment(RootComponent);
    InteractionSphere->SetSphereRadius(200.0f);
    InteractionSphere->SetRelativeLocation(FVector(0.0f, 0.0f, 100.0f));

    // Create prompt widget
    PromptWidget = CreateDefaultSubobject<UWidgetComponent>(TEXT("PromptWidget"));
    PromptWidget->SetupAttachment(RootComponent);
    PromptWidget->SetRelativeLocation(FVector(0.0f, 0.0f, 200.0f));
    PromptWidget->SetWidgetSpace(EWidgetSpace::World);
    PromptWidget->SetDrawSize(FVector2D(200.0f, 100.0f));

    // Initialize variables
    CurrentState = ECoffeeState::Idle;
    bIsBrewing = false;
    BrewTimer = 0.0f;
    bHasSugar = false;
    CoffeeCount = 0;
}

void ACoffeeMachine::BeginPlay()
{
    Super::BeginPlay();
    UpdatePromptVisibility();
}

void ACoffeeMachine::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bIsBrewing)
    {
        BrewTimer += DeltaTime;
        if (BrewTimer >= BrewTime)
        {
            // Coffee is ready
            bIsBrewing = false;
            BrewTimer = 0.0f;
            CoffeeCount++;
            UpdateState(ECoffeeState::Ready);
            OnCoffeeBrewed.Broadcast(CoffeeCount);
        }
    }
}

void ACoffeeMachine::StartBrewing()
{
    if (CurrentState == ECoffeeState::Idle)
    {
        bIsBrewing = true;
        BrewTimer = 0.0f;
        UpdateState(ECoffeeState::Brewing);
    }
}

void ACoffeeMachine::AddSugar()
{
    if (CurrentState == ECoffeeState::Ready)
    {
        bHasSugar = true;
        UpdateState(ECoffeeState::NeedsSugar);
    }
}

void ACoffeeMachine::CancelBrewing()
{
    if (bIsBrewing)
    {
        bIsBrewing = false;
        BrewTimer = 0.0f;
        UpdateState(ECoffeeState::Idle);
    }
}

void ACoffeeMachine::CollectCoffee()
{
    if (CurrentState == ECoffeeState::Ready || CurrentState == ECoffeeState::NeedsSugar)
    {
        CoffeeCount = 0;
        bHasSugar = false;
        UpdateState(ECoffeeState::Idle);
    }
}

void ACoffeeMachine::UpdateState(ECoffeeState NewState)
{
    CurrentState = NewState;
    OnCoffeeStateChanged.Broadcast(NewState);
    UpdatePromptVisibility();
}

void ACoffeeMachine::UpdatePromptVisibility()
{
    if (PromptWidget)
    {
        // Show prompt when player is near and machine is interactive
        bool bShouldShow = (CurrentState == ECoffeeState::Idle || 
                           CurrentState == ECoffeeState::Ready || 
                           CurrentState == ECoffeeState::NeedsSugar);
        
        PromptWidget->SetVisibility(bShouldShow);
    }
}